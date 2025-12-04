import os
from dotenv import load_dotenv
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

load_dotenv()

class Settings:
    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES",60))

    # Preferir siempre NON_POOLING para serverless
    raw_dsn = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL_NON_POOLING")   # 5432
        or os.getenv("POSTGRES_URL")               # 5432
        # NO usar PRISMA/POOLER (6543)
        or "sqlite:///./flazic.db"
    )

    # Normalizar esquema para SQLAlchemy + psycopg3
    if raw_dsn.startswith("postgres://"):
        raw_dsn = raw_dsn.replace("postgres://", "postgresql+psycopg://", 1)
    elif raw_dsn.startswith("postgresql://"):
        raw_dsn = raw_dsn.replace("postgresql://", "postgresql+psycopg://", 1)

    # Quitar parámetros no soportados (p.ej. pgbouncer=true)
    if raw_dsn.startswith("postgresql+psycopg://"):
        parts = urlsplit(raw_dsn)
        q = dict(parse_qsl(parts.query))
        q.pop("pgbouncer", None)  # <- elimina el flag problemático
        raw_dsn = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))

    DATABASE_URL = raw_dsn
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

    APP_NAME = os.getenv("APP_NAME", "FLAZIC-API")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 3001))

settings = Settings()