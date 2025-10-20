from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.user import User
from app.models.track import Track
from app.models.follower import Follower
from app.schemas.user import UserResponse
from app.schemas.track import TrackResponse
from app.schemas.follower import FollowerResponse, FollowerStats
from app.utils.security import get_current_user

router = APIRouter(prefix="/users", tags=["usuarios"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, description="Saltar primeros N usuarios"),
    limit: int = Query(100, description="Límite de usuarios a devolver"),
    search: Optional[str] = Query(None, description="Buscar por username o display_name"),
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener lista de usuarios - Como navegar por el directorio de artistas
    """
    try:
        # Construir query base
        query = db.query(User)
        
        # Aplicar filtro de búsqueda si existe
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) | 
                (User.display_name.ilike(f"%{search}%"))
            )
        
        # Obtener usuarios paginados
        users = query.offset(skip).limit(limit).all()
        
        return users
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener usuario específico - Como ver el perfil de un artista
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuario: {str(e)}")
    

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: dict,  # Usaremos dict para flexibilidad
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Actualizar perfil de usuario - Como editar tu información personal
    """
    try:
        # Campos permitidos para actualizar
        allowed_fields = ['display_name', 'bio', 'avatar_url', 'location', 'website_url']
        
        # Filtrar solo campos permitidos
        update_data = {key: value for key, value in user_data.items() if key in allowed_fields}
        
        # Actualizar campos
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar perfil: {str(e)}")
    

@router.get("/{user_id}/tracks", response_model=List[TrackResponse])
async def get_user_tracks(
    user_id: int,
    skip: int = Query(0, description="Saltar primeros N tracks"),
    limit: int = Query(50, description="Límite de tracks a devolver"),
    only_public: bool = Query(True, description="Solo tracks públicos"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener tracks de un usuario - Como ver la discografía de un artista
    """
    try:
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Construir query
        query = db.query(Track).filter(Track.user_id == user_id)
        
        # Filtrar por visibilidad
        if only_public:
            query = query.filter(Track.is_public == True)
        # Si el usuario actual es el dueño, mostrar todos los tracks
        elif current_user.id != user_id:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver tracks privados")
        
        tracks = query.offset(skip).limit(limit).all()
        return tracks
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener tracks: {str(e)}")

@router.get("/{user_id}/followers", response_model=List[FollowerResponse])
async def get_user_followers(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener seguidores de un usuario - Como ver la lista de fans de un artista
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        followers = db.query(Follower).filter(Follower.following_id == user_id).all()
        return followers
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener seguidores: {str(e)}")

@router.get("/{user_id}/following", response_model=List[FollowerResponse])
async def get_user_following(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener usuarios que sigue - Como ver a qué artistas sigue un usuario
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        following = db.query(Follower).filter(Follower.follower_id == user_id).all()
        return following
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener seguidos: {str(e)}")

@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener estadísticas de un usuario - Como el resumen de un perfil
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Contar seguidores
        follower_count = db.query(Follower).filter(Follower.following_id == user_id).count()
        
        # Contar seguidos
        following_count = db.query(Follower).filter(Follower.follower_id == user_id).count()
        
        # Contar tracks públicos
        track_count = db.query(Track).filter(
            Track.user_id == user_id, 
            Track.is_public == True
        ).count()
        
        return {
            "user_id": user_id,
            "follower_count": follower_count,
            "following_count": following_count,
            "track_count": track_count,
            "total_likes": sum(track.play_count for track in user.tracks if track.is_public)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")
    


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar usuario (solo admin o propio usuario)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar permisos (solo admin o el propio usuario)
        if current_user.id != user_id or not current_user.is_admin:
            raise HTTPException(status_code=403, detail="No tienes permisos")
        
        db.delete(user)
        db.commit()
        
        return {"message": "Usuario eliminado correctamente"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar usuario: {str(e)}")