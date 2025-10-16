from fastapi import APIRouter, Depends, File, Form, HTTPException, Path, Query, Response, UploadFile, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.track import Track
from app.models.user import User
from app.models.like import Like
from app.models.comment import Comment
from app.schemas.track import TrackCreate, TrackUpdate, TrackResponse
from app.schemas.like import LikeResponse, LikeStats
from app.schemas.comment import CommentResponse, CommentStats
from app.utils.security import get_current_user
import os
from pathlib import Path as PathLib  # ← Cambiar nombre para evitar conflicto

router = APIRouter(prefix="/tracks", tags=["pistas"])

UPLOAD_DIR = PathLib("uploads/audio")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_AUDIO_TYPES = {'audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-m4a'}

def allowed_audio_file(file: UploadFile) -> bool:
    return file.content_type in ALLOWED_AUDIO_TYPES




@router.get("/", response_model=List[TrackResponse])
async def get_tracks(
    skip: int = Query(0, description="Saltar primeros N tracks"),
    limit: int = Query(50, description="Límite de tracks a devolver"),
    genre: Optional[str] = Query(None, description="Filtrar por género"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    search: Optional[str] = Query(None, description="Buscar por título o descripción"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener lista de tracks - Como navegar por el catálogo musical
    """
    try:
        # Construir query base - solo tracks públicos
        query = db.query(Track).filter(Track.is_public == True)
        
        # Aplicar filtros
        if genre:
            query = query.filter(Track.genre.ilike(f"%{genre}%"))
        
        if user_id:
            query = query.filter(Track.user_id == user_id)
        
        if search:
            query = query.filter(
                (Track.title.ilike(f"%{search}%")) | 
                (Track.description.ilike(f"%{search}%"))
            )
        
        # Ordenar por más recientes primero
        tracks = query.order_by(Track.created_at.desc()).offset(skip).limit(limit).all()
        
        return tracks
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tracks: {str(e)}")

@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener track específico - Como escuchar una canción individual
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Incrementar contador de reproducciones
        track.play_count += 1
        db.commit()
        
        return track
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener track: {str(e)}")
    

@router.post("/upload-audio", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def create_track_with_audio(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    genre: Optional[str] = Form(None),
    bpm: Optional[int] = Form(None),
    is_public: bool = Form(True),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Crear track con archivo de audio local - Subir tu música desde el dispositivo
    """
    try:
        # Validar tipo de archivo
        if not allowed_audio_file(audio_file):
            raise HTTPException(
                status_code=400, 
                detail="Tipo de archivo no permitido. Use MP3, WAV, OGG o M4A"
            )
        
        # Leer el archivo
        audio_content = await audio_file.read()
        
        # Crear el track con archivo local
        new_track = Track(
            user_id=current_user.id,
            title=title,
            description=description,
            audio_url=None,  # No usar URL externa
            audio_filename=audio_file.filename,
            audio_data=audio_content,  # Guardar archivo en BD
            audio_mimetype=audio_file.content_type,
            duration_seconds=None,  # Podrías calcular esto después
            genre=genre,
            bpm=bpm,
            is_public=is_public
        )
        
        db.add(new_track)
        db.commit()
        db.refresh(new_track)
        
        return new_track
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear track con audio: {str(e)}")
    
@router.get("/{track_id}/audio")
async def get_track_audio(
    track_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener archivo de audio del track - Para reproducir la música
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        if not track.audio_data:
            raise HTTPException(status_code=404, detail="Este track no tiene archivo de audio")
        
        # Incrementar contador de reproducciones
        track.play_count += 1
        db.commit()
        
        # Devolver archivo de audio
        return Response(
            content=track.audio_data,
            media_type=track.audio_mimetype or "audio/mpeg",
            headers={
                "Content-Disposition": f'inline; filename="{track.audio_filename or "audio"}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener audio: {str(e)}")

@router.post("/", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def create_track(
    track_data: TrackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Crear nuevo track - Como subir tu propia música a la plataforma
    """
    try:
        # Validar que tenga audio_url o archivo (pero manteniendo compatibilidad)
        if not track_data.audio_url:
            raise HTTPException(
                status_code=400, 
                detail="Se requiere audio_url para este endpoint. Use /upload-audio para subir archivos."
            )
        # Crear el track
        new_track = Track(
            user_id=current_user.id,
            title=track_data.title,
            description=track_data.description,
            audio_url=track_data.audio_url,  # URL externa
            audio_filename=None,
            audio_data=None,
            audio_mimetype=None,
            duration_seconds=track_data.duration_seconds,
            genre=track_data.genre,
            bpm=track_data.bpm,
            is_public=track_data.is_public
        )
        
        db.add(new_track)
        db.commit()
        db.refresh(new_track)
        
        return new_track
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear track: {str(e)}")

@router.put("/{track_id}", response_model=TrackResponse)
async def update_track(
    track_id: int,
    track_data: TrackUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Actualizar track - Como editar los detalles de tu canción
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Verificar que el usuario es el dueño del track
        if track.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para editar este track")
        
        # Actualizar campos permitidos
        update_data = track_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(track, field, value)
        
        db.commit()
        db.refresh(track)
        
        return track
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar track: {str(e)}")

@router.delete("/{track_id}")
async def delete_track(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Eliminar track - Como quitar tu música de la plataforma
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Verificar que el usuario es el dueño del track
        if track.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este track")
        
        db.delete(track)
        db.commit()
        
        return {"message": "Track eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar track: {str(e)}")

@router.post("/{track_id}/like", response_model=LikeResponse)
async def toggle_like(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Dar/quitar like a un track - Como mostrar aprecio por una canción
    """
    try:
        # Verificar que el track existe
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Buscar like existente
        existing_like = db.query(Like).filter(
            Like.user_id == current_user.id,
            Like.track_id == track_id
        ).first()
        
        if existing_like:
            # Quitar like
            db.delete(existing_like)
            action = "removed"
        else:
            # Dar like
            new_like = Like(user_id=current_user.id, track_id=track_id)
            db.add(new_like)
            existing_like = new_like
            action = "added"
        
        db.commit()
        
        if action == "added":
            db.refresh(existing_like)
            return existing_like
        else:
            return {"message": "Like removido", "track_id": track_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al gestionar like: {str(e)}")

@router.get("/{track_id}/likes", response_model=LikeStats)
async def get_track_likes(
    track_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener estadísticas de likes de un track
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        like_count = db.query(Like).filter(Like.track_id == track_id).count()
        
        # Verificar si el usuario actual le dio like
        user_liked = db.query(Like).filter(
            Like.user_id == current_user.id,
            Like.track_id == track_id
        ).first() is not None
        
        return LikeStats(
            track_id=track_id,
            like_count=like_count,
            user_liked=user_liked
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener likes: {str(e)}")

@router.get("/{track_id}/comments", response_model=List[CommentResponse])
async def get_track_comments(
    track_id: int,
    skip: int = Query(0, description="Saltar primeros N comentarios"),
    limit: int = Query(100, description="Límite de comentarios a devolver"),
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener comentarios de un track - Como leer los comentarios de una canción
    """
    try:
        track = db.query(Track).filter(Track.id == track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Obtener comentarios principales (no respuestas)
        comments = db.query(Comment).filter(
            Comment.track_id == track_id,
            Comment.parent_comment_id == None  # Solo comentarios principales
        ).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()
        
        return comments
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener comentarios: {str(e)}")