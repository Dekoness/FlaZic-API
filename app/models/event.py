from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Event(Base):
    """Modelo de Evento - Como un cartel de concierto en la pared del club"""
    
    __tablename__ = "events"  # 🎪 El tablón de anuncios de eventos
    
    # 🆔 NÚMERO DE CARTEL (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # 👤 ORGANIZADOR (Foreign Key)
    # Qué usuario/organizador creó este evento
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 🎵 INFORMACIÓN DEL EVENTO
    # Título del evento - como "Noche de Techno" o "Live Session Acústica"
    title = Column(String(200), nullable=False, index=True)
    
    # 📝 DESCRIPCIÓN
    # Los detalles del evento - artistas, horarios, etc.
    description = Column(Text)
    
    # 📅 FECHA Y HORA DEL EVENTO
    # Cuándo será el concierto/show
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # 📍 UBICACIÓN
    # Dónde será el evento (físico o virtual)
    location = Column(String(200))
    
    # 💻 EVENTO ONLINE
    # ¿Es un evento virtual/online?
    online_event = Column(Boolean, default=False)
    
    # 🌐 URL DEL EVENTO
    # Enlace para unirse al evento online
    event_url = Column(String(500))

    cover_image_url = Column(String(500))
    
    # ⏰ FECHA DE CREACIÓN
    # Cuándo se publicó este evento
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 🔗 RELACIONES
    
    # Organizador del evento
    # organizer = relationship("User", back_populates="events")
    
    def __repr__(self):
        """Cómo se muestra este evento en los logs"""
        return f"<Event '{self.title}' on {self.event_date}>"
    
    def to_dict(self):
        """Convierte el evento a formato diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "location": self.location,
            "online_event": self.online_event,
            "event_url": self.event_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # Información del organizador
            "organizer": self.organizer.to_dict() if self.organizer else None,
            # Estado del evento (pasado/futuro)
            "is_upcoming": self.is_upcoming(),
            "is_past": self.is_past()
        }
    
    def is_upcoming(self) -> bool:
        """Verifica si el evento es futuro"""
        from datetime import datetime
        return self.event_date > datetime.now(self.event_date.tzinfo)
    
    def is_past(self) -> bool:
        """Verifica si el evento ya pasó"""
        return not self.is_upcoming()
    
    def get_event_status(self) -> str:
        """Devuelve el estado del evento como texto"""
        if self.is_upcoming():
            return "upcoming"
        return "past"