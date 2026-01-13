"""
===============================================================================
SUPABASE CLIENT.PY - Supabase Service Client
===============================================================================
A.B.E.L. Project - Supabase Integration for Auth and Database
===============================================================================
"""

import logging
from functools import lru_cache
from typing import Optional

from supabase import Client, create_client

from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client wrapper for A.B.E.L.

    Provides authenticated access to Supabase services:
    - Authentication (sign up, sign in, tokens)
    - Database (PostgreSQL)
    - Storage

    Falls back to mock mode if Supabase is unavailable.
    """

    def __init__(self, settings: Settings):
        """Initialize Supabase client with settings."""
        self.settings = settings
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None
        self._mock_mode = False
        self._initialization_error: Optional[str] = None

    @property
    def is_available(self) -> bool:
        """Check if Supabase is available (not in mock mode)."""
        return not self._mock_mode

    @property
    def client(self) -> Client:
        """Get or create Supabase client (anon key)."""
        if self._mock_mode:
            logger.warning("Supabase client accessed in mock mode - returning None")
            return None  # type: ignore

        if self._client is None:
            try:
                # Validate configuration
                if not self.settings.supabase_url:
                    raise ValueError("SUPABASE_URL is not configured")

                anon_key = self.settings.supabase_anon_key.get_secret_value()
                if not anon_key:
                    raise ValueError("SUPABASE_ANON_KEY is not configured")

                # Create client
                self._client = create_client(
                    supabase_url=self.settings.supabase_url,
                    supabase_key=anon_key,
                )
                logger.info("Supabase client initialized successfully")

            except Exception as e:
                self._initialization_error = str(e)
                logger.error(f"Failed to initialize Supabase client: {e}")

                if self.settings.allow_mock_mode:
                    logger.warning("Entering Supabase MOCK MODE - auth features will be unavailable")
                    self._mock_mode = True
                    return None  # type: ignore
                else:
                    raise

        return self._client

    @property
    def admin_client(self) -> Client:
        """Get or create Supabase admin client (service key)."""
        if self._mock_mode:
            logger.warning("Supabase admin client accessed in mock mode - returning None")
            return None  # type: ignore

        if self._admin_client is None:
            try:
                service_key = self.settings.supabase_service_key.get_secret_value()
                if service_key:
                    self._admin_client = create_client(
                        supabase_url=self.settings.supabase_url,
                        supabase_key=service_key,
                    )
                    logger.info("Supabase admin client initialized")
                else:
                    logger.warning("No service key provided, using anon client")
                    self._admin_client = self.client
            except Exception as e:
                logger.error(f"Failed to initialize Supabase admin client: {e}")
                if self.settings.allow_mock_mode:
                    self._mock_mode = True
                    return None  # type: ignore
                else:
                    raise

        return self._admin_client

    async def health_check(self) -> bool:
        """
        Check Supabase connection health.

        Returns:
            True if connection is healthy
        """
        if self._mock_mode:
            return False

        try:
            # Try to access auth to verify connection
            if self.client:
                self.client.auth.get_session()
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False


# Global instance cache
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """
    Get or create Supabase client singleton.

    Returns:
        SupabaseClient instance
    """
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        _supabase_client = SupabaseClient(settings)
    return _supabase_client


@lru_cache()
def get_supabase() -> Client:
    """
    FastAPI dependency to get Supabase client.

    Returns:
        Supabase Client instance
    """
    return get_supabase_client().client
