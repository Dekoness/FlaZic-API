from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Playlist(Base):
    """Modelo de Playlist - Como un álbum de mezclas personalizado"""
    
    __tablename__ = "playlists"  # 📚 El estante de álbumes de mezclas
    
    # 🆔 NÚMERO DE ÁLBUM (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 👤 DJ CREADOR (Foreign Key)
    # Qué usuario creó esta playlist
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 🎵 INFORMACIÓN DE LA PLAYLIST
    # Título de la playlist - como "Verano 2024" o "Fiesta Electrónica"
    title = Column(String(200), nullable=False, index=True)
    
    # 📝 DESCRIPCIÓN
    # La temática o historia detrás de esta mezcla
    description = Column(Text)
    
    # 🌍 VISIBILIDAD
    # ¿Es una playlist pública o privada?
    is_public = Column(Boolean, default=True, index=True)
    
    # 🖼️ PORTADA
    # Imagen de cover para la playlist
    cover_image_url = Column(String(500))
    
    # ⏰ FECHA DE CREACIÓN
    # Cuándo se creó esta playlist
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # DJ que creó esta playlist
    dj = relationship("User", back_populates="playlists")
    
    # Canciones incluidas en esta playlist (a través de PlaylistTrack)
    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        """Cómo se muestra esta playlist en los logs"""
        return f"<Playlist '{self.title}' by User {self.user_id}>"
    
    def to_dict(self):
        """Convierte la playlist a formato diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "is_public": self.is_public,
            "cover_image_url": self.cover_image_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "track_count": len(self.playlist_tracks),
            # Información del DJ creador
            "dj": self.dj.to_dict() if self.dj else None
        }
    
    def get_total_duration(self):
        """Calcula la duración total de la playlist en segundos"""
        return sum(track.track.duration_seconds for track in self.playlist_tracks if track.track.duration_seconds)