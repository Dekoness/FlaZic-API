from pydantic import BaseModel, validator, model_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse

class CommentBase(BaseModel):
    """Datos básicos de un comentario"""
    content: str
    timestamp_seconds: Optional[int] = None

class CommentCreate(CommentBase):
    """Datos para CREAR un nuevo comentario"""
    track_id: int
    parent_comment_id: Optional[int] = None

 
    
    @validator('content')
    def content_not_empty(cls, v):
        """Valida que el contenido no esté vacío"""
        if not v.strip():
            raise ValueError('El comentario no puede estar vacío')
        return v.strip()
    
    @validator('timestamp_seconds')
    def validate_timestamp(cls, v):
        """Valida que el timestamp sea positivo"""
        if v is not None and v < 0:
            raise ValueError('El timestamp no puede ser negativo')
        return v

class CommentUpdate(BaseModel):
    """Datos para ACTUALIZAR un comentario existente"""
    content: Optional[str] = None
    timestamp_seconds: Optional[int] = None

class CommentResponse(CommentBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    track_id: int
    user_id: int
    parent_comment_id: Optional[int] = None
    created_at: datetime
    timestamp_formatted: Optional[str]=None  # Formato mm:ss
    is_reply: bool  # Si es una respuesta
    reply_count: int  # Cuántas respuestas tiene
    author: UserResponse  # Quién escribió el comentario
    
    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def calculate_derived_fields(cls, data):
        """Calcula campos derivados automáticamente"""
        # timestamp_formatted
        if hasattr(data, 'timestamp_seconds') and data.timestamp_seconds:
            minutes = data.timestamp_seconds // 60
            seconds = data.timestamp_seconds % 60
            data.timestamp_formatted = f"{minutes}:{seconds:02d}"
        else:
            data.timestamp_formatted = ""
        
        # is_reply
        data.is_reply = data.parent_comment_id is not None
        
        # reply_count (si está disponible)
        if hasattr(data, 'replies'):
            data.reply_count = len(data.replies)
        else:
            data.reply_count = 0
            
        return data

class CommentThread(BaseModel):
    """Hilo completo de comentarios con respuestas"""
    comment: CommentResponse
    replies: List['CommentResponse'] = []  # Respuestas a este comentario

class CommentStats(BaseModel):
    """Estadísticas de comentarios para un track"""
    track_id: int
    comment_count: int  # Total de comentarios
    thread_count: int  # Comentarios principales (no respuestas)