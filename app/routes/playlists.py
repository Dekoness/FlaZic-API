from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.playlist import Playlist
from app.models.playlist_track import PlaylistTrack
from app.models.track import Track
from app.models.user import User
from app.schemas.playlist import (
    PlaylistCreate, PlaylistUpdate, PlaylistResponse,
    PlaylistTrackCreate, PlaylistTrackResponse
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/playlists", tags=["playlists"])

@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(
    skip: int = Query(0, description="Saltar primeros N playlists"),
    limit: int = Query(50, description="Límite de playlists a devolver"),
    user_id: Optional[int] = Query(None, description="Filtrar por usuario"),
    only_public: bool = Query(True, description="Solo playlists públicas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Obtener lista de playlists"""
    try:
        query = db.query(Playlist)
        
        if only_public:
            query = query.filter(Playlist.is_public == True)
        
        if user_id:
            query = query.filter(Playlist.user_id == user_id)
        
        playlists = query.order_by(Playlist.created_at.desc()).offset(skip).limit(limit).all()
        return playlists
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener playlists: {str(e)}")

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Crear nueva playlist"""
    try:
        new_playlist = Playlist(
            user_id=current_user.id,
            title=playlist_data.title,
            description=playlist_data.description,
            is_public=playlist_data.is_public,
            cover_image_url=playlist_data.cover_image_url
        )
        
        db.add(new_playlist)
        db.commit()
        db.refresh(new_playlist)
        
        return new_playlist
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear playlist: {str(e)}")

@router.post("/{playlist_id}/tracks", response_model=PlaylistTrackResponse)
async def add_track_to_playlist(
    playlist_id: int,
    track_data: PlaylistTrackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Agregar track a playlist"""
    try:
        # Verificar que la playlist existe y pertenece al usuario
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist no encontrada")
        
        if playlist.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta playlist")
        
        # Verificar que el track existe
        track = db.query(Track).filter(Track.id == track_data.track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Crear la relación
        playlist_track = PlaylistTrack(
            playlist_id=playlist_id,
            track_id=track_data.track_id,
            position=track_data.position
        )
        
        db.add(playlist_track)
        db.commit()
        db.refresh(playlist_track)
        
        return playlist_track
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al agregar track: {str(e)}")
    

@router.delete("/{playlist_id}",response_model=None)
async def delete_playlist(
    playlist_id : int,
    db: Session= Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    try:

        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist no encontrada")
        
        if playlist.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para cancelar esta playlist")
        
        db.delete(playlist)
        db.commit()

        return f'La playlist {playlist.title} ha sido eliminado exitosamente'
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar el track: {str(e)}")
    
@router.put("/{playlist_id}",response_model=PlaylistUpdate)
async def update_playlist(
    playlist_data : PlaylistUpdate,
    playlist_id : int,
    db: Session= Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:

        # Verificar que la playlist existe y pertenece al usuario
        playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if not playlist:
            raise HTTPException(status_code=404, detail="Playlist no encontrada")
        
        if playlist.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para modificar esta playlist")
        
        put_playlist = playlist_data.model_dump()
        
        for field, value in put_playlist.items():
            setattr(playlist, field, value)
        
        db.commit()
        db.refresh(playlist)
        
        return playlist
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al modificar el track: {str(e)}")