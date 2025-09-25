from pydantic import BaseSettings, PostgresDsn, RedisDsn
from typing import Optional, List
import secrets

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "mental_health"
    POSTGRES_PASSWORD: str = "secure_password"
    POSTGRES_DB: str = "mental_health_db"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_EXPIRE_SECONDS: int = 3600
    
    # Security
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://yourdomain.com"]
    ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    
    # AI & ML
    HUGGINGFACE_API_KEY: Optional[str] = None
    AI_MODEL_PATH: str = "./models/mental_health_classifier"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

