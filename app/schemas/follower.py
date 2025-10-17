from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from app.schemas.user import UserResponse

class FollowerBase(BaseModel):
    """Datos básicos de una relación de seguimiento"""
    follower_id: int
    following_id: int

class FollowerCreate(FollowerBase):
    """Datos para CREAR un nuevo seguimiento"""
    
    @validator('follower_id', 'following_id')
    def ids_must_be_different(cls, v, info):
        """Valida que no te puedas seguir a ti mismo"""
        values = info.data
        if 'follower_id' in values and 'following_id' in values:
            if values['follower_id'] == values['following_id']:
                raise ValueError('No puedes seguirte a ti mismo')
        return v

class FollowerResponse(FollowerBase):
    """Datos que ENVIAMOS al frontend"""
    id: int
    created_at: datetime
    follower: UserResponse  # Quién sigue
    following: UserResponse  # A quién siguen
    
    class Config:
        from_attributes = True

class UnfollowResponse(FollowerBase):
    message: str
    user_id: int

class FollowerStats(BaseModel):
    """Estadísticas de seguidores para un usuario"""
    user_id: int
    follower_count: int  # Cuántos te siguen
    following_count: int  # A cuántos sigues