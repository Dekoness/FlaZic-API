from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import get_db, create_tables
from app.config import settings




@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: código que se ejecuta al iniciar la app
    print("🚀 Iniciando FLAZIC-API...")
    
    # Aquí irá la conexión a la base de datos después
    print("✅ FLAZIC-API lista para recibir peticiones")
    
    yield  # La app está corriendo aquí
    
    # Shutdown: código que se ejecuta al detener la app  
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