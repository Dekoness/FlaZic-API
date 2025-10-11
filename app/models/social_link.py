from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SocialLink(Base):    
    __tablename__ = "social_links"  # 📇 El archivador de tarjetas de contacto
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # artist = relationship("User", back_populates="social_links")

    def __repr__(self):
        return f"<SocialLink {self.platform} for User {self.user_id}>"
    
    def to_dict(self):
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