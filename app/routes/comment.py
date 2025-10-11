from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.comment import Comment
from app.models.track import Track
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/comments", tags=["comentarios"])

@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Crear nuevo comentario en un track"""
    try:
        # Verificar que el track existe
        track = db.query(Track).filter(Track.id == comment_data.track_id).first()
        if not track:
            raise HTTPException(status_code=404, detail="Track no encontrado")
        
        # Verificar comentario padre si se especifica
        if comment_data.parent_comment_id:
            parent_comment = db.query(Comment).filter(
                Comment.id == comment_data.parent_comment_id
            ).first()
            if not parent_comment:
                raise HTTPException(status_code=404, detail="Comentario padre no encontrado")
        
        new_comment = Comment(
            track_id=comment_data.track_id,
            user_id=current_user.id,
            parent_comment_id=comment_data.parent_comment_id,
            content=comment_data.content,
            timestamp_seconds=comment_data.timestamp_seconds
        )
        
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        
        return new_comment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear comentario: {str(e)}")

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """🎯 Obtener comentario específico"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        return comment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener comentario: {str(e)}")

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Actualizar comentario"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para editar este comentario")
        
        update_data = comment_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)
        
        db.commit()
        db.refresh(comment)
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar comentario: {str(e)}")

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """🎯 Eliminar comentario"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este comentario")
        
        db.delete(comment)
        db.commit()
        return {"message": "Comentario eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar comentario: {str(e)}")

@router.get("/{comment_id}/replies", response_model=List[CommentResponse])
async def get_comment_replies(
    comment_id: int,
    db: Session = Depends(get_db)
):
    """🎯 Obtener respuestas de un comentario"""
    try:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        replies = db.query(Comment).filter(
            Comment.parent_comment_id == comment_id
        ).order_by(Comment.created_at.asc()).all()
        
        return replies
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener respuestas: {str(e)}")