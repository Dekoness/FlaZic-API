from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class PlaylistTrack(Base):
    """Modelo de Relación Playlist-Track - Como el índice de un álbum"""
    
    __tablename__ = "playlist_tracks"  # 📑 El índice del álbum
    
    # 🆔 NÚMERO DE ENTRADA (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 📚 ÁLBUM (Foreign Key)
    # A qué playlist pertenece esta entrada
    playlist_id = Column(Integer, ForeignKey("playlists.id"), nullable=False, index=True)
    
    # 🎵 CANCIÓN (Foreign Key)
    # Qué track está en esta posición
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    
    # 🔢 POSICIÓN EN LA LISTA
    # En qué orden va esta canción (1, 2, 3...)
    position = Column(Integer, nullable=False)
    
    # ⏰ FECHA DE AGREGADO
    # Cuándo se añadió esta canción a la playlist
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Playlist a la que pertenece
    playlist = relationship("Playlist", back_populates="playlist_tracks")
    
    # Track que está en esta posición
    track = relationship("Track", back_populates="playlist_tracks")
    
    # 🚫 RESTRICCIÓN ÚNICA
    # No puede haber la misma canción dos veces en la misma playlist
    # Y no puede haber dos canciones en la misma posición
    __table_args__ = (
        UniqueConstraint('playlist_id', 'track_id', name='uq_playlist_track'),
        UniqueConstraint('playlist_id', 'position', name='uq_playlist_position'),
    )
    
    def __repr__(self):
        """Cómo se muestra esta relación en los logs"""
        return f"<PlaylistTrack Pos {self.position} in Playlist {self.playlist_id}>"
    
    def to_dict(self):
        """Convierte la relación a formato diccionario"""
        return {
            "id": self.id,
            "playlist_id": self.playlist_id,
            "track_id": self.track_id,
            "position": self.position,
            "added_at": self.added_at.isoformat() if self.added_at else None,
            # Información completa del track
            "track": self.track.to_dict() if self.track else None
        }