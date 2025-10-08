from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class TrackBase(BaseModel):
    """Datos básicos que TODAS las pistas comparten"""
    title: str
    description: Optional[str] = None
    audio_url: str
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
    
    class Config:
        from_attributes = True