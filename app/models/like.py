from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Like(Base):
    """Modelo de Like - Como dar 'me gusta' a una canción en streaming"""
    
    __tablename__ = "likes"  # 💖 El registro de corazones/pulgares arriba
    
    # 🆔 ID DEL LIKE (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 👤 QUIÉN DA EL LIKE (Foreign Key)
    # El usuario que está expresando que le gusta el track
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 🎵 QUÉ RECIBE EL LIKE (Foreign Key)
    # El track que está recibiendo el like
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    
    # ⏰ FECHA DEL LIKE
    # Cuándo se dio el like
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Usuario que dio el like
    # user = relationship("User", back_populates="likes")
    
    # Track que recibió el like
    # track = relationship("Track", back_populates="likes")
    
    # 🚫 RESTRICCIÓN ÚNICA
    # No puedes dar like al mismo track dos veces
    __table_args__ = (
        UniqueConstraint('user_id', 'track_id', name='uq_user_track_like'),
    )
    
    def __repr__(self):
        """Cómo se muestra este like en los logs"""
        return f"<Like User {self.user_id} -> Track {self.track_id}>"
    
    def to_dict(self):
        """Convierte el like a formato diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "track_id": self.track_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Información completa del usuario y track
            "user": self.user.to_dict() if self.user else None,
            "track": self.track.to_dict() if self.track else None
        }