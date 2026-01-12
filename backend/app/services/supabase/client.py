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
    """

    def __init__(self, settings: Settings):
        """Initialize Supabase client with settings."""
        self.settings = settings
        self._client: Optional[Client] = None
        self._admin_client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """Get or create Supabase client (anon key)."""
        if self._client is None:
            self._client = create_client(
                supabase_url=self.settings.supabase_url,
                supabase_key=self.settings.supabase_anon_key.get_secret_value(),
            )
            logger.info("Supabase client initialized")
        return self._client

    @property
    def admin_client(self) -> Client:
        """Get or create Supabase admin client (service key)."""
        if self._admin_client is None:
            service_key = self.settings.supabase_service_key
            if service_key:
                self._admin_client = create_client(
                    supabase_url=self.settings.supabase_url,
                    supabase_key=service_key.get_secret_value(),
                )
                logger.info("Supabase admin client initialized")
            else:
                logger.warning("No service key provided, using anon client")
                self._admin_client = self.client
        return self._admin_client

    async def health_check(self) -> bool:
        """
        Check Supabase connection health.

        Returns:
            True if connection is healthy
        """
        try:
            # Try to access auth to verify connection
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
