from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.follower import Follower
from app.models.user import User
from app.models.notification import Notification
from app.schemas.follower import FollowerResponse, FollowerStats
from app.utils.security import get_current_user

router = APIRouter(prefix="/follow", tags=["seguidores"])

@router.post("/{user_id}", response_model=FollowerResponse)
async def toggle_follow(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Seguir/dejar de seguir usuario - Como seguir a un artista en redes sociales
    """
    try:
        # Verificar que el usuario objetivo existe
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # No puedes seguirte a ti mismo
        if user_id == current_user.id:
            raise HTTPException(status_code=400, detail="No puedes seguirte a ti mismo")
        
        # Buscar relación de seguimiento existente
        existing_follow = db.query(Follower).filter(
            Follower.follower_id == current_user.id,
            Follower.following_id == user_id
        ).first()
        
        if existing_follow:
            # Dejar de seguir
            db.delete(existing_follow)
            action = "unfollowed"
            message = f"Dejaste de seguir a {target_user.display_name or target_user.username}"
        else:
            # Seguir
            new_follow = Follower(
                follower_id=current_user.id,
                following_id=user_id
            )
            db.add(new_follow)
            
            # Crear notificación para el usuario seguido
            notification = Notification(
                user_id=user_id,  # El que recibe la notificación
                from_user_id=current_user.id,  # El que sigue
                type="follow",
                target_id=current_user.id  # ID del seguidor
            )
            db.add(notification)
            
            existing_follow = new_follow
            action = "followed"
            message = f"Empezaste a seguir a {target_user.display_name or target_user.username}"
        
        db.commit()
        
        if action == "followed":
            db.refresh(existing_follow)
            return existing_follow
        else:
            return {"message": message, "user_id": user_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al gestionar seguimiento: {str(e)}")

@router.get("/{user_id}/status")
async def get_follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Verificar estado de seguimiento - Como ver si sigues a un artista
    """
    try:
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar si el usuario actual sigue al objetivo
        is_following = db.query(Follower).filter(
            Follower.follower_id == current_user.id,
            Follower.following_id == user_id
        ).first() is not None
        
        # Verificar si el objetivo sigue al usuario actual
        is_followed_by = db.query(Follower).filter(
            Follower.follower_id == user_id,
            Follower.following_id == current_user.id
        ).first() is not None
        
        return {
            "user_id": user_id,
            "is_following": is_following,
            "is_followed_by": is_followed_by,
            "relationship": get_relationship_status(is_following, is_followed_by)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar estado: {str(e)}")

@router.get("/me/followers", response_model=List[FollowerResponse])
async def get_my_followers(
    skip: int = Query(0, description="Saltar primeros N seguidores"),
    limit: int = Query(100, description="Límite de seguidores a devolver"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener mis seguidores - Como ver mi lista de fans
    """
    try:
        followers = db.query(Follower).filter(
            Follower.following_id == current_user.id
        ).order_by(Follower.created_at.desc()).offset(skip).limit(limit).all()
        
        return followers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener seguidores: {str(e)}")

@router.get("/me/following", response_model=List[FollowerResponse])
async def get_my_following(
    skip: int = Query(0, description="Saltar primeros N seguidos"),
    limit: int = Query(100, description="Límite de seguidos a devolver"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener usuarios que sigo - Como ver mi lista de artistas favoritos
    """
    try:
        following = db.query(Follower).filter(
            Follower.follower_id == current_user.id
        ).order_by(Follower.created_at.desc()).offset(skip).limit(limit).all()
        
        return following
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener seguidos: {str(e)}")

@router.get("/me/stats", response_model=FollowerStats)
async def get_my_follow_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener mis estadísticas de seguimiento - Como ver mis métricas sociales
    """
    try:
        # Contar seguidores
        follower_count = db.query(Follower).filter(
            Follower.following_id == current_user.id
        ).count()
        
        # Contar seguidos
        following_count = db.query(Follower).filter(
            Follower.follower_id == current_user.id
        ).count()
        
        return FollowerStats(
            user_id=current_user.id,
            follower_count=follower_count,
            following_count=following_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.get("/suggestions", response_model=List[FollowerResponse])
async def get_follow_suggestions(
    limit: int = Query(10, description="Límite de sugerencias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener sugerencias de usuarios a seguir - Como descubrir nuevos artistas
    """
    try:
        # Usuarios que no sigues y tienen muchos seguidores
        suggestions = db.query(User).filter(
            User.id != current_user.id,
            ~User.id.in_(
                db.query(Follower.following_id).filter(
                    Follower.follower_id == current_user.id
                )
            )
        ).order_by(
            # Ordenar por popularidad (más seguidores primero)
            db.query(Follower).filter(Follower.following_id == User.id).count().desc()
        ).limit(limit).all()
        
        # Convertir a formato de respuesta de follower
        follower_responses = []
        for user in suggestions:
            follower_response = FollowerResponse(
                id=0,  # No es una relación real aún
                follower_id=current_user.id,
                following_id=user.id,
                created_at=user.created_at,
                follower=current_user,
                following=user
            )
            follower_responses.append(follower_response)
        
        return follower_responses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener sugerencias: {str(e)}")

def get_relationship_status(is_following: bool, is_followed_by: bool) -> str:
    """
    🎯 Determinar el estado de la relación entre usuarios
    """
    if is_following and is_followed_by:
        return "mutual"  # Se siguen mutuamente
    elif is_following:
        return "following"  # Solo tú les sigues
    elif is_followed_by:
        return "follower"  # Solo ellos te siguen
    else:
        return "none"  # No hay relación