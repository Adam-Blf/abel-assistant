"""
A.B.E.L - Configuration Settings
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="A.B.E.L", description="Application name")
    app_env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(default="", description="Secret key")
    api_version: str = Field(default="v1", description="API version")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Database
    database_url: str = Field(
        default="",
        description="PostgreSQL connection URL",
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Qdrant Vector DB
    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection: str = Field(default="abel_memories", description="Qdrant collection name")

    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model"
    )

    # ElevenLabs TTS
    elevenlabs_api_key: str = Field(default="", description="ElevenLabs API key")
    elevenlabs_voice_id: str = Field(default="", description="ElevenLabs voice ID")

    # Google APIs
    google_client_id: str = Field(default="", description="Google OAuth client ID")
    google_client_secret: str = Field(default="", description="Google OAuth client secret")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/auth/google/callback",
        description="Google OAuth redirect URI",
    )

    # Twitter/X
    twitter_api_key: str = Field(default="", description="Twitter API key")
    twitter_api_secret: str = Field(default="", description="Twitter API secret")
    twitter_access_token: str = Field(default="", description="Twitter access token")
    twitter_access_secret: str = Field(default="", description="Twitter access secret")
    twitter_bearer_token: str = Field(default="", description="Twitter bearer token")

    # Instagram
    instagram_username: str = Field(default="", description="Instagram username")
    instagram_password: str = Field(default="", description="Instagram password")

    # Weather
    openweather_api_key: str = Field(default="", description="OpenWeatherMap API key")

    # News
    news_api_key: str = Field(default="", description="News API key")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate secret key is set in production."""
        if info.data.get("app_env") == "production" and not v:
            raise ValueError("SECRET_KEY must be set in production environment")
        if info.data.get("app_env") == "production" and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate database URL is set in production."""
        if info.data.get("app_env") == "production" and not v:
            raise ValueError("DATABASE_URL must be set in production environment")
        return v


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
