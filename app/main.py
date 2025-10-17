from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes import users, tracks, follow, comment, events, notifications, playlists, social_links
from app.routes.auth import router as auth_router
from app.database import create_tables
from app.config import settings
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando FLAZIC-API...")
    print(f"📍 Entorno: {settings.ENVIRONMENT}")
    
    try:
        create_tables()
        print("✅ Tablas creadas/verificadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
    
    print("🎵 FLAZIC-API lista para recibir peticiones")
    yield
    print("🔌 Cerrando FLAZIC-API...")

app = FastAPI(
    title="FLAZIC-API",
    description="API para plataforma de música FLAZIC",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ⬇️ MODIFICADO: CORS mejorado para producción
origins = settings.CORS_ORIGINS
if not origins and settings.ENVIRONMENT == "development":
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(tracks.router)
app.include_router(follow.router)
app.include_router(comment.router)
app.include_router(playlists.router)
# app.include_router(notifications.router)
# app.include_router(events.router)
# app.include_router(social_links.router)
# Cargar variables de entorno
@app.get("/")
async def root():
    return {
        "message": "🎵 Bienvenido a FLAZIC-API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "users": "/api/users",
            "tracks": "/api/tracks"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FLAZIC-API", "environment": settings.ENVIRONMENT}

@app.get("/api/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"message": "✅ Base de datos conectada", "environment": settings.ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))  # Usa PORT de Railway o 3001 por defecto
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)