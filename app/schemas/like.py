from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.track import TrackResponse

class LikeBase(BaseModel):
    """Datos básicos de un like"""
    user_id: int
    track_id: int

class LikeCreate(LikeBase):
    """Datos para CREAR un nuevo like"""
    pass

class LikeResponse(LikeBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    created_at: datetime
    user: UserResponse  # Quién dio el like
    track: TrackResponse  # Qué track recibió el like
    
    class Config:
        from_attributes = True

class LikeStats(BaseModel):
    """Estadísticas de likes para un track"""
    track_id: int
    like_count: int  # Cuántos likes tiene
    user_liked: bool  # Si el usuario actual le dio like