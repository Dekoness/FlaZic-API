from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models.event import Event
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventSummary
from app.utils.security import get_current_user

router = APIRouter(prefix="/events", tags=["eventos"])

@router.get("/", response_model=List[EventSummary])
async def get_events(
    skip: int = Query(0, description="Saltar primeros N eventos"),
    limit: int = Query(50, description="Límite de eventos a devolver"),
    upcoming_only: bool = Query(True, description="Solo eventos futuros"),
    user_id: Optional[int] = Query(None, description="Filtrar por organizador"),
    online_only: Optional[bool] = Query(None, description="Solo eventos online"),
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener lista de eventos - Como ver el calendario de conciertos
    """
    try:
        query = db.query(Event)
        
        if upcoming_only:
            query = query.filter(Event.event_date > datetime.now())
        else:
            query = query.filter(Event.event_date <= datetime.now())
        
        if user_id:
            query = query.filter(Event.user_id == user_id)
        
        if online_only is not None:
            query = query.filter(Event.online_event == online_only)
        
        events = query.order_by(Event.event_date.asc()).offset(skip).limit(limit).all()
        return events
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener eventos: {str(e)}")

@router.post("/", response_model=EventResponse)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Crear nuevo evento - Como anunciar tu propio concierto
    """
    try:
        new_event = Event(
            user_id=current_user.id,
            title=event_data.title,
            description=event_data.description,
            event_date=event_data.event_date,
            location=event_data.location,
            online_event=event_data.online_event,
            event_url=event_data.event_url,
            cover_image_url=event_data.cover_image_url
        )
        
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        
        return new_event
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear evento: {str(e)}")

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """
    🎯 Obtener evento específico - Como ver los detalles de un concierto
    """
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener evento: {str(e)}")

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Actualizar evento - Como editar los detalles de tu concierto
    """
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        if event.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para editar este evento")
        
        update_data = event_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(event, field, value)
        
        db.commit()
        db.refresh(event)
        
        return event
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar evento: {str(e)}")

@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🎯 Eliminar evento - Como cancelar un concierto anunciado
    """
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        
        if event.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="No tienes permisos para eliminar este evento")
        
        db.delete(event)
        db.commit()
        
        return {"message": "Evento eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar evento: {str(e)}")