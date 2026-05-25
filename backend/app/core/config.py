from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Leak Detector"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite for development to keep things simple
    # Can be swapped for PostgreSQL in production
    DATABASE_URL: str = "sqlite+aiosqlite:///../database/leak_detector.db"
    
    # Security
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"  # In prod, read from env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # ML Model Path
    MODEL_PATH: str = "ml_models/churn_model_v1.joblib"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
