from pydantic import BaseModel, field_validator
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
    
    @field_validator('content')
    def content_not_empty(cls, v):
        """Valida que el contenido no esté vacío"""
        if not v.strip():
            raise ValueError('El comentario no puede estar vacío')
        return v.strip()
    
    @field_validator('timestamp_seconds')
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
    timestamp_formatted: str  # Formato mm:ss
    is_reply: bool  # Si es una respuesta
    reply_count: int  # Cuántas respuestas tiene
    author: UserResponse  # Quién escribió el comentario
    
    class Config:
        from_attributes = True

class CommentThread(BaseModel):
    """Hilo completo de comentarios con respuestas"""
    comment: CommentResponse
    replies: List['CommentResponse'] = []  # Respuestas a este comentario

class CommentStats(BaseModel):
    """Estadísticas de comentarios para un track"""
    track_id: int
    comment_count: int  # Total de comentarios
    thread_count: int  # Comentarios principales (no respuestas)