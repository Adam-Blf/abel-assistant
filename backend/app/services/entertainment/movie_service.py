"""
A.B.E.L - Movie & TV Service
Integrates TMDB, OMDB, TVMaze
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class MovieService:
    """
    Movie & TV service integrating:
    - TMDB (The Movie Database)
    - OMDB (Open Movie Database)
    - TVMaze (TV Shows)
    """

    TMDB_API = "https://api.themoviedb.org/3"
    OMDB_API = "http://www.omdbapi.com"
    TVMAZE_API = "https://api.tvmaze.com"
    TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"

    def __init__(self):
        self.tmdb_key = getattr(settings, 'tmdb_api_key', '')
        self.omdb_key = getattr(settings, 'omdb_api_key', '')

    # ========================================
    # TMDB API
    # ========================================
    async def tmdb_search_movies(
        self,
        query: str,
        year: Optional[int] = None,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search movies on TMDB"""
        try:
            params = {
                "api_key": self.tmdb_key,
                "query": query,
                "page": page,
                "language": "fr-FR",
            }
            if year:
                params["year"] = year

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/search/movie",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TMDB search error: {e}")
        return {"results": []}

    async def tmdb_search_tv(
        self,
        query: str,
        page: int = 1,
    ) -> Dict[str, Any]:
        """Search TV shows on TMDB"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/search/tv",
                    params={
                        "api_key": self.tmdb_key,
                        "query": query,
                        "page": page,
                        "language": "fr-FR",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TMDB TV search error: {e}")
        return {"results": []}

    async def tmdb_get_movie(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get movie details from TMDB"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/movie/{movie_id}",
                    params={
                        "api_key": self.tmdb_key,
                        "language": "fr-FR",
                        "append_to_response": "credits,videos,similar,recommendations",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TMDB movie error: {e}")
        return None

    async def tmdb_get_trending(
        self,
        media_type: str = "movie",  # movie, tv, all
        time_window: str = "week",  # day, week
    ) -> List[Dict[str, Any]]:
        """Get trending movies/TV shows"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/trending/{media_type}/{time_window}",
                    params={"api_key": self.tmdb_key, "language": "fr-FR"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"TMDB trending error: {e}")
        return []

    async def tmdb_get_popular(
        self,
        media_type: str = "movie",
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Get popular movies/TV shows"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/{media_type}/popular",
                    params={
                        "api_key": self.tmdb_key,
                        "page": page,
                        "language": "fr-FR",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"TMDB popular error: {e}")
        return []

    async def tmdb_get_genres(
        self,
        media_type: str = "movie",
    ) -> List[Dict[str, Any]]:
        """Get genre list"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/genre/{media_type}/list",
                    params={"api_key": self.tmdb_key, "language": "fr-FR"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("genres", [])
        except Exception as e:
            logger.error(f"TMDB genres error: {e}")
        return []

    async def tmdb_discover(
        self,
        media_type: str = "movie",
        genre_id: Optional[int] = None,
        year: Optional[int] = None,
        sort_by: str = "popularity.desc",
        page: int = 1,
    ) -> List[Dict[str, Any]]:
        """Discover movies/TV with filters"""
        try:
            params = {
                "api_key": self.tmdb_key,
                "sort_by": sort_by,
                "page": page,
                "language": "fr-FR",
            }
            if genre_id:
                params["with_genres"] = genre_id
            if year:
                params["year"] = year

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TMDB_API}/discover/{media_type}",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"TMDB discover error: {e}")
        return []

    # ========================================
    # TVMAZE API (FREE - No auth)
    # ========================================
    async def tvmaze_search(self, query: str) -> List[Dict[str, Any]]:
        """Search TV shows on TVMaze"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TVMAZE_API}/search/shows",
                    params={"q": query},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TVMaze search error: {e}")
        return []

    async def tvmaze_get_show(self, show_id: int) -> Optional[Dict[str, Any]]:
        """Get show details from TVMaze"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TVMAZE_API}/shows/{show_id}",
                    params={"embed[]": ["episodes", "cast"]},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TVMaze show error: {e}")
        return None

    async def tvmaze_schedule(
        self,
        country: str = "FR",
        date: Optional[str] = None,  # YYYY-MM-DD
    ) -> List[Dict[str, Any]]:
        """Get TV schedule"""
        try:
            params = {"country": country}
            if date:
                params["date"] = date

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.TVMAZE_API}/schedule",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"TVMaze schedule error: {e}")
        return []

    # ========================================
    # RECOMMENDATIONS
    # ========================================
    async def get_recommendations(
        self,
        genre: Optional[str] = None,
        mood: Optional[str] = None,
        media_type: str = "movie",
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations"""
        # Map moods to genres
        mood_genres = {
            "happy": [35, 10751],  # Comedy, Family
            "sad": [18, 10749],  # Drama, Romance
            "excited": [28, 12, 878],  # Action, Adventure, Sci-Fi
            "scary": [27, 53],  # Horror, Thriller
            "relaxed": [16, 10751, 10402],  # Animation, Family, Music
        }

        if mood and mood.lower() in mood_genres:
            genre_ids = mood_genres[mood.lower()]
            results = []
            for gid in genre_ids[:2]:
                movies = await self.tmdb_discover(media_type, genre_id=gid, page=1)
                results.extend(movies[:5])
            return results

        if genre:
            genres = await self.tmdb_get_genres(media_type)
            genre_id = next(
                (g["id"] for g in genres if genre.lower() in g["name"].lower()),
                None
            )
            if genre_id:
                return await self.tmdb_discover(media_type, genre_id=genre_id)

        # Default: trending
        return await self.tmdb_get_trending(media_type)

    def get_image_url(
        self,
        path: str,
        size: str = "w500",  # w92, w154, w185, w342, w500, w780, original
    ) -> str:
        """Get full image URL from TMDB path"""
        if not path:
            return ""
        return f"{self.TMDB_IMAGE_BASE}/{size}{path}"
