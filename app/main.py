from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes import users, tracks, follow, comment, events, notifications, playlists, social_links
from app.routes.auth import router as auth_router
from app.database import create_tables
from .database import init_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando FLAZIC-API...")
    print("✅ FLAZIC-API lista para recibir peticiones")
    
    try:
        init_engine()
    except Exception:
        # Deja trazas en logs y evita ocultar el error
        raise
    try:
        create_tables()
        print("✅ Tablas creadas exitosamente")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
    
    print("🎵 FLAZIC-API lista para recibir peticiones")
    yield
    print("🔌 Cerrando FLAZIC-API...")

# Crear aplicación FastAPI
app = FastAPI(
    title="FLAZIC-API",
    description="API para plataforma de música FLAZIC",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI en /docs
    redoc_url="/redoc",  # Redoc en /redoc
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(users.router)
app.include_router(tracks.router)
app.include_router(follow.router)
app.include_router(comment.router)
app.include_router(playlists.router)
app.include_router(notifications.router)
# app.include_router(events.router)
# app.include_router(social_links.router)


# Configurar CORS (para conectar con frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambiar a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint raíz
@app.get("/")
async def root():
    return {
        "message": "🎵 Bienvenido a FLAZIC-API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "users": "/api/users",
            "tracks": "/api/tracks"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FLAZIC-API"}

@app.get("/api/db-test")
async def db_test(db: Session = Depends(get_db)):
    """Prueba que la base de datos funciona"""
    # db es tu "ayudante de cocina" listo para trabajar
    return {"message": "✅ Base de datos conectada", "db_type": str(type(db))}

