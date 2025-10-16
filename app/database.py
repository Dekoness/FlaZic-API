from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# ⬇️ MODIFICADO: Soporte para PostgreSQL y SQLite
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
    # PostgreSQL (producción)
    engine = create_engine(settings.DATABASE_URL)
else:
    # SQLite (desarrollo)
    engine = create_engine(
        settings.DATABASE_URL or "sqlite:///./flazic.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)