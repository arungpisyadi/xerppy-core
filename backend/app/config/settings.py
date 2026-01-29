"""Application Settings using Pydantic Settings"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Xerppy API"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./xerppy.db"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: list = ["http://localhost:5173"]
    
    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8003
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
