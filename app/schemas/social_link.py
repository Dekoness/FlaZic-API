from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional
from datetime import datetime
from app.models.social_link import SocialLink

class SocialLinkBase(BaseModel):
    """Datos básicos de un enlace social"""
    platform: str
    url: str

class SocialLinkCreate(SocialLinkBase):
    """Datos para CREAR un nuevo enlace social"""
    
    @field_validator('platform')
    def validate_platform(cls, v):
        """Valida que la plataforma sea soportada"""
        valid_platforms = [
            'spotify', 'youtube', 'instagram', 'twitter', 
            'tiktok', 'soundcloud', 'bandcamp', 'apple_music',
            'facebook', 'twitch', 'website'
        ]
        if v.lower() not in valid_platforms:
            raise ValueError(f'Plataforma no soportada. Usa: {", ".join(valid_platforms)}')
        return v.lower()
    
    @field_validator('url')
    def validate_url(cls, v):
        """Valida que la URL sea válida para la plataforma"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('La URL debe comenzar con http:// o https://')
        return v

class SocialLinkUpdate(BaseModel):
    """Datos para ACTUALIZAR un enlace social existente"""
    platform: Optional[str] = None
    url: Optional[str] = None

class SocialLinkResponse(SocialLinkBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    user_id: int
    created_at: datetime
    icon: str  # Emoji del icono de la plataforma
    
    class Config:
        from_attributes = True
    
    @classmethod
    def model_validate(cls, obj):
        """Añade el icono automáticamente al validar"""
        data = super().model_validate(obj)
        data.icon = SocialLink.get_platform_icon(data.platform)
        return data