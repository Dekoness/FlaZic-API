from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.social_link import SocialLink
from app.models.user import User
from app.schemas.social_link import SocialLinkCreate, SocialLinkUpdate, SocialLinkResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/social-links", tags=["redes-sociales"])

@router.get("/user/{user_id}", response_model=List[SocialLinkResponse])
async def get_user_social_links(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener enlaces sociales de un usuario - Como ver las redes de un artista
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        social_links = db.query(SocialLink).filter(SocialLink.user_id == user_id).all()
        return social_links
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener enlaces sociales: {str(e)}")

@router.post("/", response_model=SocialLinkResponse)
async def create_social_link(
    social_data: SocialLinkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Agregar enlace social - Como conectar tu perfil de Spotify/YouTube
    """
    try:
        # Verificar que no existe ya un enlace para esta plataforma
        existing_link = db.query(SocialLink).filter(
            SocialLink.user_id == current_user.id,
            SocialLink.platform == social_data.platform
        ).first()
        
        if existing_link:
            raise HTTPException(status_code=400, detail="Ya tienes un enlace para esta plataforma")
        
        new_social_link = SocialLink(
            user_id=current_user.id,
            platform=social_data.platform,
            url=social_data.url
        )
        
        db.add(new_social_link)
        db.commit()
        db.refresh(new_social_link)
        
        return new_social_link
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear enlace social: {str(e)}")

@router.put("/{social_link_id}", response_model=SocialLinkResponse)
async def update_social_link(
    social_link_id: int,
    social_data: SocialLinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Actualizar enlace social - Como cambiar tu URL de Instagram
    """
    try:
        social_link = db.query(SocialLink).filter(SocialLink.id == social_link_id).first()
        
        if not social_link:
            raise HTTPException(status_code=404, detail="Enlace social no encontrado")
        
        if social_link.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para editar este enlace")
        
        update_data = social_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(social_link, field, value)
        
        db.commit()
        db.refresh(social_link)
        
        return social_link
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar enlace social: {str(e)}")

@router.delete("/{social_link_id}")
async def delete_social_link(
    social_link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Eliminar enlace social - Como quitar una red social de tu perfil
    """
    try:
        social_link = db.query(SocialLink).filter(SocialLink.id == social_link_id).first()
        
        if not social_link:
            raise HTTPException(status_code=404, detail="Enlace social no encontrado")
        
        if social_link.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este enlace")
        
        db.delete(social_link)
        db.commit()
        
        return {"message": "Enlace social eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar enlace social: {str(e)}")