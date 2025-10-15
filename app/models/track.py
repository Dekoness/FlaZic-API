from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Track(Base):

    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer,  ForeignKey("users.id"), nullable=False, index=True)
    artist = relationship("User", back_populates="tracks", foreign_keys=[user_id])
    title = Column(String(200), nullable=False, index=True )
    description = Column(Text)
    audio_url= Column(String(500), nullable=False)
    duration_seconds= Column(Integer)
    genre= Column(String(50), index=True)
    bpm= Column(Integer)
    is_public= Column(Boolean, default=True, index=True)
    play_count= Column(Integer, default=0)
    created_at= Column(DateTime(timezone=True), server_default=func.now())
    updated_at= Column(DateTime(timezone=True), onupdate=func.now())
    comments = relationship("Comment", back_populates="track", cascade="all, delete-orphan")
    playlist_tracks = relationship("PlaylistTrack", back_populates="track", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="track", cascade="all, delete-orphan")



    def __repr__(self):
        return f"<Track '{self.title}' by User {self.user_id}>"
    
    def to_dict(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "audio_url": self.audio_url,
            "duration_seconds": self.duration_seconds,
            "genre": self.genre,
            "bpm": self.bpm,
            "is_public": self.is_public,
            "play_count": self.play_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "artist": self.artist.to_dict() if hasattr(self, 'artist') and self.artist else None
        }
    
    def increment_play_count(self):
        self.play_count += 1