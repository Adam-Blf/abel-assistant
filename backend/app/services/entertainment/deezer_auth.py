"""
A.B.E.L - Deezer OAuth Service
Authentification et accès au compte utilisateur Deezer.
"""

import os
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx

from app.core.logging import logger


class DeezerAuthService:
    """
    Service d'authentification Deezer OAuth 2.0.
    Permet d'accéder aux playlists, favoris et données du compte.
    """

    AUTH_URL = "https://connect.deezer.com/oauth/auth.php"
    TOKEN_URL = "https://connect.deezer.com/oauth/access_token.php"
    API_URL = "https://api.deezer.com"

    def __init__(self):
        self.app_id = os.getenv("DEEZER_APP_ID")
        self.secret_key = os.getenv("DEEZER_SECRET_KEY")
        self.redirect_uri = os.getenv(
            "DEEZER_REDIRECT_URI",
            "http://localhost:8000/api/auth/deezer/callback"
        )
        self.access_token: Optional[str] = None

    def get_auth_url(self, perms: str = "basic_access,email,manage_library,listening_history") -> str:
        """
        Génère l'URL d'autorisation OAuth.

        Permissions disponibles:
        - basic_access: Infos profil
        - email: Adresse email
        - offline_access: Token permanent
        - manage_library: Playlists, favoris
        - manage_community: Amis, commentaires
        - delete_library: Supprimer du contenu
        - listening_history: Historique d'écoute
        """
        params = {
            "app_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "perms": perms,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> Optional[str]:
        """Échange le code OAuth contre un access token."""
        params = {
            "app_id": self.app_id,
            "secret": self.secret_key,
            "code": code,
            "output": "json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.TOKEN_URL, params=params)
                data = response.json()

                if "access_token" in data:
                    self.access_token = data["access_token"]
                    logger.info("Deezer: Token obtenu avec succès")
                    return self.access_token
                else:
                    logger.error(f"Deezer auth error: {data}")
                    return None

        except Exception as e:
            logger.error(f"Deezer exchange_code error: {e}")
            return None

    async def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Effectue une requête authentifiée à l'API Deezer."""
        if not self.access_token:
            logger.error("Deezer: Pas de token d'accès")
            return None

        params = params or {}
        params["access_token"] = self.access_token

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.API_URL}{endpoint}", params=params)
                return response.json()
        except Exception as e:
            logger.error(f"Deezer API error: {e}")
            return None

    # === PROFIL ===

    async def get_me(self) -> Optional[Dict]:
        """Récupère le profil de l'utilisateur connecté."""
        return await self._request("/user/me")

    # === PLAYLISTS ===

    async def get_my_playlists(self, limit: int = 25) -> Optional[Dict]:
        """Récupère les playlists de l'utilisateur."""
        return await self._request("/user/me/playlists", {"limit": limit})

    async def get_playlist(self, playlist_id: int) -> Optional[Dict]:
        """Récupère les détails d'une playlist."""
        return await self._request(f"/playlist/{playlist_id}")

    async def create_playlist(self, title: str) -> Optional[Dict]:
        """Crée une nouvelle playlist."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_URL}/user/me/playlists",
                params={"access_token": self.access_token, "title": title}
            )
            return response.json()

    async def add_to_playlist(self, playlist_id: int, track_ids: list) -> bool:
        """Ajoute des tracks à une playlist."""
        songs = ",".join(map(str, track_ids))
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_URL}/playlist/{playlist_id}/tracks",
                params={"access_token": self.access_token, "songs": songs}
            )
            return response.json() == True

    # === FAVORIS ===

    async def get_my_tracks(self, limit: int = 50) -> Optional[Dict]:
        """Récupère les tracks favoris."""
        return await self._request("/user/me/tracks", {"limit": limit})

    async def get_my_albums(self, limit: int = 25) -> Optional[Dict]:
        """Récupère les albums favoris."""
        return await self._request("/user/me/albums", {"limit": limit})

    async def get_my_artists(self, limit: int = 25) -> Optional[Dict]:
        """Récupère les artistes favoris."""
        return await self._request("/user/me/artists", {"limit": limit})

    async def add_favorite_track(self, track_id: int) -> bool:
        """Ajoute un track aux favoris."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.API_URL}/user/me/tracks",
                params={"access_token": self.access_token, "track_id": track_id}
            )
            return response.json() == True

    async def remove_favorite_track(self, track_id: int) -> bool:
        """Retire un track des favoris."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.API_URL}/user/me/tracks",
                params={"access_token": self.access_token, "track_id": track_id}
            )
            return response.json() == True

    # === HISTORIQUE ===

    async def get_listening_history(self, limit: int = 50) -> Optional[Dict]:
        """Récupère l'historique d'écoute."""
        return await self._request("/user/me/history", {"limit": limit})

    # === RECOMMANDATIONS ===

    async def get_recommendations(self) -> Optional[Dict]:
        """Récupère les recommandations personnalisées."""
        return await self._request("/user/me/recommendations/tracks")

    async def get_flow(self) -> Optional[Dict]:
        """Récupère le Flow personnalisé."""
        return await self._request("/user/me/flow")


# Instance globale
deezer_auth = DeezerAuthService()
