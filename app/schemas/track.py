from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class TrackBase(BaseModel):
    """Datos básicos que TODAS las pistas comparten"""
    title: str
    description: Optional[str] = None
    audio_url: Optional[str] = None  # Cambiar a opcional
    duration_seconds: Optional[int] = None
    genre: Optional[str] = None
    bpm: Optional[int] = None
    is_public: bool = True

class TrackCreate(TrackBase):
    """Datos para CREAR una nueva pista"""
    pass

class TrackUpdate(BaseModel):
    """Datos para ACTUALIZAR una pista existente"""
    title: Optional[str] = None
    description: Optional[str] = None
    audio_url: Optional[str] = None  # Agregar para actualización
    genre: Optional[str] = None
    bpm: Optional[int] = None
    is_public: Optional[bool] = None

class TrackResponse(TrackBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    user_id: int
    play_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    artist: Optional[UserResponse] = None
    audio_filename: Optional[str] = None
    has_audio_file: bool = False
    
    class Config:
        from_attributes = True