"""
===============================================================================
SETTINGS.PY - Application Configuration
===============================================================================
A.B.E.L. Project - Environment Configuration with pydantic-settings
CRITICAL: All secrets loaded from environment variables
===============================================================================
"""

from functools import lru_cache
from typing import List

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All sensitive values use SecretStr to prevent accidental logging.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # APP SETTINGS
    # -------------------------------------------------------------------------
    app_name: str = "ABEL"
    app_env: str = Field(default="development", pattern="^(development|staging|production)$")
    debug: bool = False
    log_level: str = "INFO"

    # -------------------------------------------------------------------------
    # SERVER
    # -------------------------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000

    # -------------------------------------------------------------------------
    # SECURITY (CRITICAL)
    # -------------------------------------------------------------------------
    secret_key: SecretStr = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 30
    session_timeout_minutes: int = 15

    # For mobile apps, use "*" in production or specific domains
    cors_origins: str = "*"
    trusted_hosts: str = "*"

    rate_limit_enabled: bool = True

    # -------------------------------------------------------------------------
    # SUPABASE
    # -------------------------------------------------------------------------
    supabase_url: str = ""
    supabase_anon_key: SecretStr = SecretStr("")
    supabase_service_key: SecretStr = SecretStr("")

    # -------------------------------------------------------------------------
    # GOOGLE GEMINI
    # -------------------------------------------------------------------------
    gemini_api_key: SecretStr = SecretStr("")
    gemini_model_chat: str = "gemini-1.5-flash"
    gemini_model_vision: str = "gemini-1.5-pro"

    # -------------------------------------------------------------------------
    # EXTERNAL APIS
    # -------------------------------------------------------------------------
    openweather_api_key: SecretStr | None = None
    news_api_key: SecretStr | None = None

    # -------------------------------------------------------------------------
    # LOGGING
    # -------------------------------------------------------------------------
    log_format: str = "json"
    log_pii_redaction: bool = True

    # -------------------------------------------------------------------------
    # COMPUTED PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def trusted_hosts_list(self) -> List[str]:
        """Parse trusted hosts from comma-separated string."""
        return [host.strip() for host in self.trusted_hosts.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    # -------------------------------------------------------------------------
    # VALIDATORS
    # -------------------------------------------------------------------------

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        """Ensure secret key is strong enough."""
        if len(v.get_secret_value()) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings
    """
    return Settings()
