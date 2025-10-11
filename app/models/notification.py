from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Notification(Base):
    """Modelo de Notificación - Como las alertas de actividad en redes sociales"""
    
    __tablename__ = "notifications"  # 🔔 El centro de notificaciones
    
    # 🆔 ID DE LA NOTIFICACIÓN (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 👤 DESTINATARIO (Foreign Key)
    # El usuario que recibe la notificación
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 👤 REMITENTE (Foreign Key)
    # El usuario que causó la notificación (quien siguió, comentó, etc.)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 📢 TIPO DE NOTIFICACIÓN
    # Qué acción generó la notificación
    type = Column(String(50), nullable=False, index=True)  # 'follow', 'comment', 'like', 'track_comment'
    
    # 🎯 ELEMENTO RELACIONADO
    # ID del track, comentario, etc. que causó la notificación
    target_id = Column(Integer, nullable=True)  # Puede ser track_id, comment_id, etc.
    
    # 📬 ESTADO DE LECTURA
    # Si la notificación ya fue vista por el usuario
    is_read = Column(Boolean, default=False, index=True)
    
    # ⏰ FECHA DE CREACIÓN
    # Cuándo se generó la notificación
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Usuario que recibe la notificación
    # recipient = relationship("User", foreign_keys=[user_id], back_populates="notifications_received")
    
    # Usuario que causó la notificación
    # sender = relationship("User", foreign_keys=[from_user_id], back_populates="notifications_sent")
    
    def __repr__(self):
        """Cómo se muestra esta notificación en los logs"""
        return f"<Notification {self.type} from User {self.from_user_id} to User {self.user_id}>"
    
    def to_dict(self):
        """Convierte la notificación a formato diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "from_user_id": self.from_user_id,
            "type": self.type,
            "target_id": self.target_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Información del remitente
            "sender": self.sender.to_dict() if self.sender else None,
            # Mensaje formateado para mostrar
            "message": self.get_message(),
            "icon": self.get_icon()
        }
    
    def get_message(self) -> str:
        """Genera el mensaje de la notificación según el tipo"""
        messages = {
            'follow': f"{self.sender.display_name or self.sender.username} empezó a seguirte",
            'like': f"A {self.sender.display_name or self.sender.username} le gusta tu track",
            'comment': f"{self.sender.display_name or self.sender.username} comentó en tu track",
            'track_comment': f"{self.sender.display_name or self.sender.username} comentó en un track que sigues",
            'new_track': f"{self.sender.display_name or self.sender.username} publicó un nuevo track"
        }
        return messages.get(self.type, "Nueva notificación")
    
    def get_icon(self) -> str:
        """Devuelve el emoji correspondiente al tipo de notificación"""
        icons = {
            'follow': '👤',
            'like': '❤️', 
            'comment': '💬',
            'track_comment': '🎵',
            'new_track': '🎶'
        }
        return icons.get(self.type, '🔔')
    
    def mark_as_read(self):
        """Marca la notificación como leída"""
        self.is_read = True