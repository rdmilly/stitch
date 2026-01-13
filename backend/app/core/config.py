from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Content Forge"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://contentforge:password@db:5432/contentforge"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    
    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    
    # LinkedIn
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:8000/api/auth/linkedin/callback"
    
    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
