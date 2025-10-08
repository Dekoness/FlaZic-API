from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SocialLink(BaseModel):
    """Modelo de Enlace Social - Como una tarjeta de contacto para redes sociales"""
    
    __tablename__ = "social_links"  # 📇 El archivador de tarjetas de contacto
    
    # 🆔 NÚMERO DE TARJETA (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 👤 PROPIETARIO (Foreign Key)
    # A qué artista pertenece este enlace social
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 📱 PLATAFORMA SOCIAL
    # Qué red social es (Spotify, YouTube, Instagram, etc.)
    platform = Column(String(50), nullable=False, index=True)
    
    # 🌐 URL DEL PERFIL
    # El enlace directo al perfil del artista
    url = Column(String(500), nullable=False)
    
    # ⏰ FECHA DE CREACIÓN
    # Cuándo se agregó este enlace social
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Artista dueño de este enlace
    artist = relationship("User", back_populates="social_links")
    
    def __repr__(self):
        """Cómo se muestra este enlace social en los logs"""
        return f"<SocialLink {self.platform} for User {self.user_id}>"
    
    def to_dict(self):
        """Convierte la tarjeta social a formato diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "platform": self.platform,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def get_platform_icon(cls, platform: str) -> str:
        """Devuelve el icono correspondiente a cada plataforma"""
        icons = {
            "spotify": "🎵",
            "youtube": "📺", 
            "instagram": "📸",
            "twitter": "🐦",
            "tiktok": "🎵",
            "soundcloud": "☁️",
            "bandcamp": "🎸",
            "apple_music": "🎧"
        }
        return icons.get(platform.lower(), "🔗")