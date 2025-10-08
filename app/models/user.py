from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(500))
    location = Column(String(100))
    website_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    tracks = relationship("Track", back_populates="artist", cascade="all, delete-orphan")
    social_links = relationship("SocialLink", back_populates="artist", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.email})"
    
    def to_dict(self):
        return {
            "id":self.id,
            "username":self.username,
            "email":self.email,
            "display_name":self.display_name,
            "bio":self.bio,
            "avatar_url":self.avatar_url,
            "location":self.location,
            "website_url":self.website_url,
            "created_at":self.created_at.isoformat() if self.created_at else None
        } 
    

    