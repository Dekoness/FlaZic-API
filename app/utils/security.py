from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import os

from app.config import settings
from app.database import get_db
from app.models.user import User

# 🔐 OBTENER SALT DEL .env
ARGON2_SALT = os.getenv("ARGON2_SALT", "default_salt_seguro_cambiar_en_produccion")

# 🔐 CONFIGURACIÓN ARGON2 (más moderno y seguro que bcrypt)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=3,      # Más rápido en desarrollo
    argon2__memory_cost=65536,# 64MB de memoria
    argon2__parallelism=1,    # 1 hilo
    argon2__hash_len=32       # Longitud del hash
)

def create_password_hash(password: str) -> str:
    """Crea hash seguro con Argon2 + Salt del .env"""
    return pwd_context.hash(password + ARGON2_SALT)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña con Argon2 + Salt del .env"""
    return pwd_context.verify(plain_password + ARGON2_SALT, hashed_password)

# 🎫 JWT (se mantiene igual)
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user(token: str = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    payload = verify_token(token.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user