from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.utils.security import (
    create_password_hash, 
    verify_password, 
    create_access_token,
    verify_token
)
from datetime import timedelta


router = APIRouter(prefix="/auth", tags=["autentificacion"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse, response_model_exclude_none=True, status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(status_code=400, detail="Este nombre de usuario ya está registrado")
        else:
            raise HTTPException(status_code=400, detail="Este email ya está registrado")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        display_name=user_data.display_name or user_data.username,
        password_hash=create_password_hash(user_data.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Asegura valores generados por el servidor
    if new_user.created_at is None:
        new_user = db.query(User).filter(User.id == new_user.id).first()

    return UserResponse.model_validate(new_user)

@router.post("/login")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(
        (User.email == login_data.email) | 
        (User.username == login_data.email)
    ).first()

    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )
    

    access_token = create_access_token(
        data={"sub": str(user.id)},  # "sub" = subject (quién es el usuario)
        expires_delta=timedelta(minutes= settings.JWT_EXPIRE_MINUTES)
    )
    
    return {
        "message": "Login exitoso",
        "user": UserResponse.model_validate(user),
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout():

    return {"message": "Logout exitoso - Token debe ser eliminado del frontend"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(security), 
    db: Session = Depends(get_db)
):
    
    print(f"🔍 Token recibido: {token}")
    print(f"🔍 Credentials: {token.credentials}")

    payload = verify_token(token.credentials)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )
    

    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user