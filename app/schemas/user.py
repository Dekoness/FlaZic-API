from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime



class UserBase(BaseModel):
    username:str
    email: str
    display_name : Optional[str] = None

class UserCreate(UserBase):
    password: str
    password_confirm: str

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    @field_validator('password_confirm')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v
    

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):

    id: int
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True  