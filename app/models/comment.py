from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Comment(Base):
    """Modelo de Comentario - Como comentar en un punto específico de un video de YouTube"""
    
    __tablename__ = "comments"  # 💬 El hilo de conversación
    
    # 🆔 ID DEL COMENTARIO (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 🎵 CANCIÓN COMENTADA (Foreign Key)
    # El track que está recibiendo el comentario
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False, index=True)
    
    # 👤 AUTOR DEL COMENTARIO (Foreign Key)
    # El usuario que escribió el comentario
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 🔁 COMENTARIO PADRE (Foreign Key - Respuestas)
    # Si es una respuesta a otro comentario (hilos)
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    # 📝 CONTENIDO DEL COMENTARIO
    # El texto del comentario
    content = Column(Text, nullable=False)
    
    # ⏱️ MARCA DE TIEMPO
    # En qué segundo de la canción se hizo el comentario (como en SoundCloud)
    timestamp_seconds = Column(Integer)
    
    # ⏰ FECHA DEL COMENTARIO
    # Cuándo se publicó el comentario
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Track comentado
    # track = relationship("Track", back_populates="comments")
    
    # Autor del comentario
    # author = relationship("User", back_populates="comments")
    
    # Comentario padre (si es respuesta)
    # parent = relationship("Comment", remote_side=[id], back_populates="replies")
    
    # Respuestas a este comentario
    # replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan")
    
    def __repr__(self):
        """Cómo se muestra este comentario en los logs"""
        timestamp = f"at {self.timestamp_seconds}s" if self.timestamp_seconds else ""
        return f"<Comment by User {self.user_id} on Track {self.track_id} {timestamp}>"
    
    def to_dict(self):
        """Convierte el comentario a formato diccionario"""
        return {
            "id": self.id,
            "track_id": self.track_id,
            "user_id": self.user_id,
            "parent_comment_id": self.parent_comment_id,
            "content": self.content,
            "timestamp_seconds": self.timestamp_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Información completa del autor
            "author": self.author.to_dict() if self.author else None,
            # Si tiene respuestas
            "reply_count": len(self.replies) if self.replies else 0,
            # Información del comentario padre (si es respuesta)
            "parent_comment": self.parent.to_dict() if self.parent else None
        }
    
    def is_reply(self) -> bool:
        """Verifica si este comentario es una respuesta"""
        return self.parent_comment_id is not None
    
    def get_timestamp_formatted(self) -> str:
        """Devuelve el timestamp en formato mm:ss"""
        if not self.timestamp_seconds:
            return ""
        minutes = self.timestamp_seconds // 60
        seconds = self.timestamp_seconds % 60
        return f"{minutes}:{seconds:02d}"