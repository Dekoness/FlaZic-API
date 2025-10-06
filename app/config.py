import os
from dotenv import load_dotenv


load_dotenv()

class Settings:
    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES",60))

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./flazic.db")

    APP_NAME = os.getenv("APP_NAME", "FLAZIC-API")
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 3001))

settings = Settings()