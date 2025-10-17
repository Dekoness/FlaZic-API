
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserResponse
from app.schemas.track import TrackResponse

class PlaylistBase(BaseModel):
    """Datos básicos de una playlist"""
    title: str
    description: Optional[str] = None
    is_public: bool = True
    cover_image_url: Optional[str] = None

class PlaylistCreate(PlaylistBase):
    """Datos para CREAR una nueva playlist"""
    pass

class PlaylistUpdate(BaseModel):
    """Datos para ACTUALIZAR una playlist existente"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image_url: Optional[str] = None

class PlaylistTrackBase(BaseModel):
    """Datos básicos de una canción en playlist"""
    track_id: int
    position: int

class PlaylistTrackCreate(PlaylistTrackBase):
    """Datos para AGREGAR una canción a playlist"""
    pass

class PlaylistTrackResponse(PlaylistTrackBase):
    """Respuesta de canción en playlist"""
    id: int
    added_at: datetime
    track: TrackResponse
    
    class Config:
        from_attributes = True

class PlaylistResponse(PlaylistBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    user_id: int
    created_at: datetime
    track_count: int= 0
    total_duration: Optional[int] = None
    dj: Optional[UserResponse]=None
    tracks: List[PlaylistTrackResponse] = []
    
    class Config:
        from_attributes = True