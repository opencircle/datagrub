"""
Configuration module for PromptForge API
Uses Pydantic Settings for environment variable management
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "PromptForge API"
    VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://promptforge:promptforge@localhost:5432/promptforge"
    DATABASE_ECHO: bool = False  # Set to True to see SQL queries

    # Database Connection Pool (Performance Optimization)
    DB_POOL_SIZE: int = 20              # Base connection pool size
    DB_MAX_OVERFLOW: int = 30            # Additional connections when needed
    DB_POOL_RECYCLE: int = 3600         # Recycle connections after 1 hour
    DB_POOL_PRE_PING: bool = True       # Verify connection health before use
    DB_POOL_TIMEOUT: int = 30           # Timeout for getting connection from pool
    DB_ECHO_POOL: bool = False          # Log connection pool events

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 300  # 5 minutes default cache TTL

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-strong-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Git Integration
    GIT_REPOS_PATH: str = "/tmp/promptforge-repos"

    # Evaluation
    EVALUATION_TIMEOUT_SECONDS: int = 300  # 5 minutes

    # Model Provider Encryption
    # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    MODEL_PROVIDER_ENCRYPTION_KEY: str = "vF8k9mN2pQ5wX7zC3bH6jL4tR1yU8sA0dG2iK5nM9oP3qT6vW4xZ7cB1eF3hJ5="

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
