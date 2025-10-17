from pydantic import BaseModel, EmailStr, model_validator, root_validator, validator
from typing import Optional
from datetime import datetime



class UserBase(BaseModel):
    username:str
    email: EmailStr
    display_name : Optional[str] = None

class UserCreate(UserBase):
    password: str
    password_confirm: str

    @model_validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    @model_validator(check_fields=False)
    def passwords_match(cls, values):
        if 'password' in values and values['password'] != values:
            raise ValueError('Las contraseñas no coinciden')
        return values
    

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