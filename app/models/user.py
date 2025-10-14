from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

from app.models.follower import Follower
from app.models.notification import Notification

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
    # social_links = relationship("SocialLink", back_populates="artist", cascade="all, delete-orphan")
    # events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    # playlists = relationship("Playlist", back_populates="dj", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")

    # notifications_received = relationship("Notification",  foreign_keys=[Notification.user_id], 
    #                                       back_populates="recipient",
    #                                       cascade="all, delete-orphan")
    # notifications_sent = relationship("Notification",
    #                                     foreign_keys=[Notification.from_user_id],
    #                                     back_populates="sender",
    #                                     cascade="all, delete-orphan")

    followers = relationship("Follower", foreign_keys=[Follower.following_id], 
                            back_populates="following",
                            cascade="all, delete-orphan")
    following = relationship("Follower", foreign_keys=[Follower.follower_id], 
                            back_populates="follower",
                            cascade="all, delete-orphan")
    

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
    

    