"""Application Settings using Pydantic Settings"""
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Xerppy API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database Type Selection
    database_type: Literal["sqlite", "postgresql", "mysql"] = "sqlite"

    # PostgreSQL Settings
    postgresql_host: str = "localhost"
    postgresql_port: int = 5432
    postgresql_user: str = "postgres"
    postgresql_password: str = "password"
    postgresql_db: str = "xerppy"

    # MySQL Settings
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_db: str = "xerppy"

    # SQLite Settings
    sqlite_path: str = "./xerppy.db"

    # Connection Pool Settings
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_echo: bool = False
    database_pool_pre_ping: bool = True

    # Legacy Database URL (for backward compatibility)
    # If provided, this takes precedence over individual database settings
    database_url: str = ""

    @property
    def built_database_url(self) -> str:
        """
        Build the database URL based on the selected database type.
        Returns the legacy database_url if it's provided, otherwise builds from settings.
        """
        # If legacy database_url is provided, use it
        if self.database_url:
            return self.database_url

        # Build URL based on database type
        if self.database_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite_path}"
        elif self.database_type == "postgresql":
            return (
                f"postgresql+asyncpg://{self.postgresql_user}:{self.postgresql_password}"
                f"@{self.postgresql_host}:{self.postgresql_port}/{self.postgresql_db}"
            )
        elif self.database_type == "mysql":
            return (
                f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
            )
        else:
            # Fallback to SQLite
            return f"sqlite+aiosqlite:///{self.sqlite_path}"

    @property
    def effective_database_url(self) -> str:
        """
        Deprecated: Use built_database_url instead.
        Kept for backward compatibility.
        """
        return self.built_database_url

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:5173"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8003

    @property
    def parsed_cors_origins(self):
        """Parse comma-separated CORS origins into a list"""
        if isinstance(self.cors_origins, list):
            return self.cors_origins
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
