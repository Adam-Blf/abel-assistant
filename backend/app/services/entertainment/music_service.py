"""
A.B.E.L - Music Service
Integrates Spotify, Deezer, Last.fm, and more
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class MusicService:
    """
    Music service integrating multiple APIs:
    - Deezer (free, no auth required for search)
    - Spotify (requires OAuth)
    - Last.fm (requires API key)
    - iTunes Search (free)
    - MusicBrainz (free)
    """

    # API URLs
    DEEZER_API = "https://api.deezer.com"
    SPOTIFY_API = "https://api.spotify.com/v1"
    LASTFM_API = "http://ws.audioscrobbler.com/2.0"
    ITUNES_API = "https://itunes.apple.com"
    MUSICBRAINZ_API = "https://musicbrainz.org/ws/2"
    LYRICS_API = "https://api.lyrics.ovh/v1"

    def __init__(self):
        self.spotify_token: Optional[str] = None

    # ========================================
    # DEEZER API (FREE - No auth required)
    # ========================================
    async def deezer_search(
        self,
        query: str,
        search_type: str = "track",  # track, album, artist, playlist
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Search on Deezer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/search/{search_type}",
                    params={"q": query, "limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Deezer search error: {e}")
        return []

    async def deezer_get_track(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Get track details from Deezer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/track/{track_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Deezer track error: {e}")
        return None

    async def deezer_get_artist(self, artist_id: int) -> Optional[Dict[str, Any]]:
        """Get artist details from Deezer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/artist/{artist_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Deezer artist error: {e}")
        return None

    async def deezer_get_album(self, album_id: int) -> Optional[Dict[str, Any]]:
        """Get album details from Deezer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/album/{album_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Deezer album error: {e}")
        return None

    async def deezer_get_playlist(self, playlist_id: int) -> Optional[Dict[str, Any]]:
        """Get playlist from Deezer"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/playlist/{playlist_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Deezer playlist error: {e}")
        return None

    async def deezer_get_charts(self, limit: int = 50) -> Dict[str, Any]:
        """Get Deezer charts"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/chart/0/tracks",
                    params={"limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Deezer charts error: {e}")
        return {}

    async def deezer_get_genres(self) -> List[Dict[str, Any]]:
        """Get all Deezer genres"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/genre",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Deezer genres error: {e}")
        return []

    async def deezer_radio(self, genre_id: int = 0) -> List[Dict[str, Any]]:
        """Get radio tracks by genre"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.DEEZER_API}/radio/{genre_id}/tracks",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Deezer radio error: {e}")
        return []

    # ========================================
    # ITUNES API (FREE - No auth required)
    # ========================================
    async def itunes_search(
        self,
        query: str,
        media: str = "music",  # music, movie, podcast, audiobook
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Search on iTunes"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ITUNES_API}/search",
                    params={
                        "term": query,
                        "media": media,
                        "limit": limit,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"iTunes search error: {e}")
        return []

    # ========================================
    # LYRICS API (FREE)
    # ========================================
    async def get_lyrics(self, artist: str, title: str) -> Optional[str]:
        """Get song lyrics"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.LYRICS_API}/{artist}/{title}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("lyrics")
        except Exception as e:
            logger.error(f"Lyrics error: {e}")
        return None

    # ========================================
    # MUSICBRAINZ API (FREE - No auth)
    # ========================================
    async def musicbrainz_search(
        self,
        query: str,
        search_type: str = "artist",  # artist, release, recording
    ) -> List[Dict[str, Any]]:
        """Search on MusicBrainz"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.MUSICBRAINZ_API}/{search_type}",
                    params={"query": query, "fmt": "json"},
                    headers={"User-Agent": "ABEL/1.0 (abel@assistant.ai)"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get(f"{search_type}s", [])
        except Exception as e:
            logger.error(f"MusicBrainz error: {e}")
        return []

    # ========================================
    # UNIFIED SEARCH
    # ========================================
    async def search_music(
        self,
        query: str,
        sources: List[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across multiple music sources"""
        sources = sources or ["deezer", "itunes"]
        results = {}

        for source in sources:
            if source == "deezer":
                results["deezer"] = await self.deezer_search(query)
            elif source == "itunes":
                results["itunes"] = await self.itunes_search(query)
            elif source == "musicbrainz":
                results["musicbrainz"] = await self.musicbrainz_search(query, "recording")

        return results

    async def get_recommendations(
        self,
        artist: Optional[str] = None,
        genre: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get music recommendations"""
        if genre:
            # Get genre-based recommendations from Deezer
            genres = await self.deezer_get_genres()
            genre_id = next(
                (g["id"] for g in genres if genre.lower() in g["name"].lower()),
                0
            )
            return await self.deezer_radio(genre_id)

        if artist:
            # Search for similar artists
            artists = await self.deezer_search(artist, "artist", limit=1)
            if artists:
                artist_id = artists[0]["id"]
                artist_data = await self.deezer_get_artist(artist_id)
                if artist_data and "tracklist" in artist_data:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(artist_data["tracklist"], timeout=10.0)
                        if response.status_code == 200:
                            return response.json().get("data", [])

        # Default: return charts
        charts = await self.deezer_get_charts()
        return charts.get("data", [])
