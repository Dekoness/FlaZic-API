from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationStats
from app.utils.security import get_current_user

router = APIRouter(prefix="/notifications", tags=["notificaciones"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, description="Saltar primeros N notificaciones"),
    limit: int = Query(50, description="Límite de notificaciones a devolver"),
    unread_only: bool = Query(False, description="Solo notificaciones no leídas"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener notificaciones del usuario - Como revisar tu bandeja de alertas
    """
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user.id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        return notifications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notificaciones: {str(e)}")

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Marcar notificación como leída - Como marcar un mensaje como visto
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id  # Solo puede marcar sus propias notificaciones
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        notification.mark_as_read()
        db.commit()
        db.refresh(notification)
        
        return notification
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al marcar notificación: {str(e)}")

@router.put("/read-all", response_model=dict)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Marcar todas las notificaciones como leídas - Como limpiar toda la bandeja
    """
    try:
        # Obtener todas las notificaciones no leídas del usuario
        unread_notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).all()
        
        # Marcar todas como leídas
        for notification in unread_notifications:
            notification.mark_as_read()
        
        db.commit()
        
        return {
            "message": f"Todas las notificaciones marcadas como leídas",
            "notifications_updated": len(unread_notifications)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al marcar notificaciones: {str(e)}")

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Obtener estadísticas de notificaciones - Como ver tu resumen de alertas
    """
    try:
        total_count = db.query(Notification).filter(
            Notification.user_id == current_user.id
        ).count()
        
        unread_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()
        
        return NotificationStats(
            user_id=current_user.id,
            unread_count=unread_count,
            total_count=total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Eliminar notificación - Como quitar una alerta de tu bandeja
    """
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notificación no encontrada")
        
        db.delete(notification)
        db.commit()
        
        return {"message": "Notificación eliminada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar notificación: {str(e)}")