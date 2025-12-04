from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = None
SessionLocal = None
Base = declarative_base()

def init_engine():
    global engine, SessionLocal
    if engine:
        return
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        print(f"[DB] Connected using {settings.DATABASE_URL.split('?')[0]}")
    except Exception as e:
        # Loguea la causa real en Vercel
        import traceback; traceback.print_exc()
        raise

def get_db():
    if not SessionLocal:
        init_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)