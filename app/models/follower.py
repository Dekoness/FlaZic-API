from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Follower(Base):
    """Modelo de Seguidor - Como seguir a un artista en redes sociales"""
    
    __tablename__ = "followers"  # 📋 La lista de seguidores
    
    # 🆔 ID DE LA CONEXIÓN (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 🙋 QUIÉN SIGUE (Foreign Key)
    # El usuario que está siguiendo a alguien (el fan)
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 🎤 A QUIÉN SIGUE (Foreign Key)  
    # El usuario que está siendo seguido (el artista)
    following_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # ⏰ FECHA DE SEGUIMIENTO
    # Cuándo empezó a seguir a este artista
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES - Conexiones bidireccionales
    
    # El seguidor (quién sigue)
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    
    # El seguido (a quién siguen)
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")
    
    # 🚫 RESTRICCIÓN ÚNICA
    # No puedes seguir a la misma persona dos veces
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following'),
    )
    
    def __repr__(self):
        """Cómo se muestra esta relación en los logs"""
        return f"<Follower {self.follower_id} -> {self.following_id}>"
    
    def to_dict(self):
        """Convierte la relación a formato diccionario"""
        return {
            "id": self.id,
            "follower_id": self.follower_id,
            "following_id": self.following_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Información completa de ambos usuarios
            "follower": self.follower.to_dict() if self.follower else None,
            "following": self.following.to_dict() if self.following else None
        }