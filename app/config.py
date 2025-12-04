import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES",60))

    # Usar DSN real de Postgres si existe
    raw_dsn = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or os.getenv("POSTGRES_PRISMA_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")
        or "sqlite:///./flazic.db"
    )

    # Normaliza esquema para SQLAlchemy + psycopg3
    if raw_dsn.startswith("postgres://"):
        raw_dsn = raw_dsn.replace("postgres://", "postgresql+psycopg://", 1)
    DATABASE_URL = raw_dsn
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

    APP_NAME = os.getenv("APP_NAME", "FLAZIC-API")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 3001))

settings = Settings()