from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class NotificationBase(BaseModel):
    """Datos básicos de una notificación"""
    user_id: int
    from_user_id: int
    type: str
    target_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    """Datos para CREAR una nueva notificación"""
    
    @field_validator('type')
    def validate_type(cls, v):
        """Valida que el tipo de notificación sea soportado"""
        valid_types = ['follow', 'like', 'comment', 'track_comment', 'new_track']
        if v not in valid_types:
            raise ValueError(f'Tipo de notificación no válido. Usa: {", ".join(valid_types)}')
        return v

class NotificationUpdate(BaseModel):
    """Datos para ACTUALIZAR una notificación existente"""
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    is_read: bool
    created_at: datetime
    message: str  # Mensaje formateado
    icon: Optional[str]=None  # Emoji del icono
    sender: UserResponse  # Quién causó la notificación
    
    class Config:
        from_attributes = True

class NotificationStats(BaseModel):
    """Estadísticas de notificaciones para un usuario"""
    user_id: int
    unread_count: int  # Notificaciones no leídas
    total_count: int  # Total de notificaciones