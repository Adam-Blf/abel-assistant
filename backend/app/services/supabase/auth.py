"""
===============================================================================
SUPABASE AUTH.PY - Authentication Service
===============================================================================
A.B.E.L. Project - User Authentication via Supabase Auth
===============================================================================
"""

import logging
from dataclasses import dataclass
from typing import Optional

from gotrue.errors import AuthApiError
from supabase import Client

from app.core.exceptions import ABELException
from app.services.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class AuthUser:
    """Authenticated user data."""

    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class AuthTokens:
    """Authentication tokens."""

    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


@dataclass
class AuthResult:
    """Authentication result with user and tokens."""

    user: AuthUser
    tokens: AuthTokens


class AuthService:
    """
    Authentication service using Supabase Auth.

    Handles:
    - User registration
    - User login
    - Token refresh
    - Password reset
    - User profile
    """

    def __init__(self):
        """Initialize auth service."""
        self._client: Optional[Client] = None
        self._supabase_client = None

    @property
    def is_available(self) -> bool:
        """Check if auth service is available."""
        if self._supabase_client is None:
            self._supabase_client = get_supabase_client()
        return self._supabase_client.is_available

    @property
    def client(self) -> Client:
        """Get Supabase client."""
        if self._client is None:
            self._supabase_client = get_supabase_client()
            self._client = self._supabase_client.client
        return self._client

    def _check_availability(self):
        """Check if auth service is available, raise error if not."""
        if not self.is_available:
            raise ABELException(
                status_code=503,
                error_code="SERVICE_UNAVAILABLE",
                message="Authentication service is temporarily unavailable. Please try again later.",
            )

    async def register(
        self,
        email: str,
        password: str,
        name: Optional[str] = None,
    ) -> AuthResult:
        """
        Register a new user.

        Args:
            email: User email
            password: User password
            name: Optional user name

        Returns:
            AuthResult with user and tokens

        Raises:
            ABELException: If registration fails
        """
        self._check_availability()

        try:
            # Build user metadata
            metadata = {}
            if name:
                metadata["name"] = name

            # Sign up with Supabase
            response = self.client.auth.sign_up(
                {
                    "email": email,
                    "password": password,
                    "options": {"data": metadata},
                }
            )

            if response.user is None:
                raise ABELException(
                    status_code=400,
                    error_code="REGISTRATION_FAILED",
                    message="Registration failed. Please try again.",
                )

            # Check if email confirmation is required
            if response.session is None:
                # Email confirmation required
                raise ABELException(
                    status_code=200,
                    error_code="CONFIRM_EMAIL",
                    message="Please check your email to confirm your account.",
                )

            user = AuthUser(
                id=response.user.id,
                email=response.user.email or email,
                name=response.user.user_metadata.get("name"),
                created_at=str(response.user.created_at),
            )

            tokens = AuthTokens(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
            )

            logger.info(f"User registered: {user.id}")
            return AuthResult(user=user, tokens=tokens)

        except AuthApiError as e:
            logger.warning(f"Registration error: {e.message}")
            raise ABELException(
                status_code=400,
                error_code="REGISTRATION_ERROR",
                message=self._translate_auth_error(e.message),
            )
        except ABELException:
            raise
        except Exception as e:
            logger.error(f"Unexpected registration error: {e}")
            raise ABELException(
                status_code=500,
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred during registration.",
            )

    async def login(self, email: str, password: str) -> AuthResult:
        """
        Login user with email and password.

        Args:
            email: User email
            password: User password

        Returns:
            AuthResult with user and tokens

        Raises:
            ABELException: If login fails
        """
        self._check_availability()

        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if response.user is None or response.session is None:
                raise ABELException(
                    status_code=401,
                    error_code="LOGIN_FAILED",
                    message="Invalid email or password.",
                )

            user = AuthUser(
                id=response.user.id,
                email=response.user.email or email,
                name=response.user.user_metadata.get("name"),
                created_at=str(response.user.created_at),
            )

            tokens = AuthTokens(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
            )

            logger.info(f"User logged in: {user.id}")
            return AuthResult(user=user, tokens=tokens)

        except AuthApiError as e:
            logger.warning(f"Login error: {e.message}")
            raise ABELException(
                status_code=401,
                error_code="LOGIN_ERROR",
                message=self._translate_auth_error(e.message),
            )
        except ABELException:
            raise
        except Exception as e:
            logger.error(f"Unexpected login error: {e}")
            raise ABELException(
                status_code=500,
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred during login.",
            )

    async def refresh_token(self, refresh_token: str) -> AuthTokens:
        """
        Refresh access token.

        Args:
            refresh_token: Current refresh token

        Returns:
            New AuthTokens

        Raises:
            ABELException: If refresh fails
        """
        try:
            response = self.client.auth.refresh_session(refresh_token)

            if response.session is None:
                raise ABELException(
                    status_code=401,
                    error_code="REFRESH_FAILED",
                    message="Session expired. Please login again.",
                )

            tokens = AuthTokens(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=response.session.expires_in or 3600,
            )

            logger.debug("Token refreshed successfully")
            return tokens

        except AuthApiError as e:
            logger.warning(f"Token refresh error: {e.message}")
            raise ABELException(
                status_code=401,
                error_code="REFRESH_ERROR",
                message="Session expired. Please login again.",
            )
        except ABELException:
            raise
        except Exception as e:
            logger.error(f"Unexpected refresh error: {e}")
            raise ABELException(
                status_code=500,
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
            )

    async def get_user(self, access_token: str) -> AuthUser:
        """
        Get user from access token.

        Args:
            access_token: JWT access token

        Returns:
            AuthUser

        Raises:
            ABELException: If token is invalid
        """
        try:
            response = self.client.auth.get_user(access_token)

            if response.user is None:
                raise ABELException(
                    status_code=401,
                    error_code="INVALID_TOKEN",
                    message="Invalid or expired token.",
                )

            return AuthUser(
                id=response.user.id,
                email=response.user.email or "",
                name=response.user.user_metadata.get("name"),
                created_at=str(response.user.created_at),
            )

        except AuthApiError as e:
            logger.warning(f"Get user error: {e.message}")
            raise ABELException(
                status_code=401,
                error_code="INVALID_TOKEN",
                message="Invalid or expired token.",
            )
        except ABELException:
            raise
        except Exception as e:
            logger.error(f"Unexpected get_user error: {e}")
            raise ABELException(
                status_code=500,
                error_code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
            )

    async def logout(self, access_token: str) -> None:
        """
        Logout user (invalidate token).

        Args:
            access_token: JWT access token
        """
        try:
            self.client.auth.sign_out()
            logger.debug("User logged out")
        except Exception as e:
            logger.warning(f"Logout error (non-critical): {e}")

    async def request_password_reset(self, email: str) -> None:
        """
        Request password reset email.

        Args:
            email: User email
        """
        try:
            self.client.auth.reset_password_email(email)
            logger.info(f"Password reset requested for: {email}")
        except Exception as e:
            # Don't reveal if email exists
            logger.warning(f"Password reset error: {e}")

    def _translate_auth_error(self, message: str) -> str:
        """Translate Supabase auth errors to user-friendly messages."""
        translations = {
            "Invalid login credentials": "Email ou mot de passe incorrect.",
            "Email not confirmed": "Veuillez confirmer votre email.",
            "User already registered": "Cet email est déjà utilisé.",
            "Password should be at least 6 characters": "Le mot de passe doit contenir au moins 6 caractères.",
            "Unable to validate email address": "Adresse email invalide.",
        }
        return translations.get(message, message)


# Global auth service instance
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get or create AuthService singleton."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
