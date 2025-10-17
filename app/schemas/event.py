from pydantic import BaseModel, validator, HttpUrl
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class EventBase(BaseModel):
    """Datos básicos de un evento"""
    title: str
    description: Optional[str] = None
    event_date: datetime
    location: Optional[str] = None
    online_event: bool = False
    event_url: Optional[str] = None
    cover_image_url: Optional[str] = None

class EventCreate(EventBase):
    """Datos para CREAR un nuevo evento"""
    
    @validator('event_date')
    def event_date_must_be_future(cls, v):
        """Valida que la fecha del evento sea futura"""
        if v <= datetime.now():
            raise ValueError('La fecha del evento debe ser futura')
        return v
    
    @validator('event_url')
    def validate_event_url(cls, v):
        """Valida que la URL sea válida si se proporciona"""
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('La URL del evento debe comenzar con http:// o https://')
        return v

class EventUpdate(BaseModel):
    """Datos para ACTUALIZAR un evento existente"""
    title: Optional[str] = None
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    online_event: Optional[bool] = None
    event_url: Optional[str] = None

class EventResponse(EventBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    user_id: int
    created_at: datetime
    is_upcoming: bool
    is_past: bool
    event_status: str
    organizer: UserResponse
    
    class Config:
        from_attributes = True

class EventSummary(BaseModel):
    """Resumen de evento para listas"""
    id: int
    title: str
    event_date: datetime
    location: Optional[str] = None
    online_event: bool
    is_upcoming: bool
    
    class Config:
        from_attributes = True