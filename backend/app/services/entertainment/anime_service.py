"""
A.B.E.L - Anime & Manga Service
Integrates Jikan (MyAnimeList), AniList, Kitsu
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.logging import logger


class AnimeService:
    """
    Anime & Manga service integrating:
    - Jikan (MyAnimeList unofficial API)
    - AniList GraphQL API
    - Kitsu API
    """

    JIKAN_API = "https://api.jikan.moe/v4"
    KITSU_API = "https://kitsu.io/api/edge"
    ANILIST_API = "https://graphql.anilist.co"

    # ========================================
    # JIKAN API (MyAnimeList - FREE)
    # ========================================
    async def jikan_search_anime(
        self,
        query: str,
        page: int = 1,
        limit: int = 25,
        sfw: bool = True,
    ) -> Dict[str, Any]:
        """Search anime on MyAnimeList via Jikan"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/anime",
                    params={
                        "q": query,
                        "page": page,
                        "limit": limit,
                        "sfw": sfw,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Jikan anime search error: {e}")
        return {"data": []}

    async def jikan_search_manga(
        self,
        query: str,
        page: int = 1,
        limit: int = 25,
    ) -> Dict[str, Any]:
        """Search manga on MyAnimeList via Jikan"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/manga",
                    params={"q": query, "page": page, "limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Jikan manga search error: {e}")
        return {"data": []}

    async def jikan_get_anime(self, mal_id: int) -> Optional[Dict[str, Any]]:
        """Get anime details from MAL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/anime/{mal_id}/full",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
        except Exception as e:
            logger.error(f"Jikan anime error: {e}")
        return None

    async def jikan_get_manga(self, mal_id: int) -> Optional[Dict[str, Any]]:
        """Get manga details from MAL"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/manga/{mal_id}/full",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
        except Exception as e:
            logger.error(f"Jikan manga error: {e}")
        return None

    async def jikan_top_anime(
        self,
        filter_type: str = "airing",  # airing, upcoming, bypopularity, favorite
        page: int = 1,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Get top anime"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/top/anime",
                    params={"filter": filter_type, "page": page, "limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Jikan top anime error: {e}")
        return []

    async def jikan_seasonal_anime(
        self,
        year: int = 2024,
        season: str = "winter",  # winter, spring, summer, fall
    ) -> List[Dict[str, Any]]:
        """Get seasonal anime"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/seasons/{year}/{season}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Jikan seasonal error: {e}")
        return []

    async def jikan_anime_recommendations(self, mal_id: int) -> List[Dict[str, Any]]:
        """Get anime recommendations"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/anime/{mal_id}/recommendations",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Jikan recommendations error: {e}")
        return []

    async def jikan_get_genres(self) -> List[Dict[str, Any]]:
        """Get all anime genres"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/genres/anime",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Jikan genres error: {e}")
        return []

    async def jikan_random_anime(self) -> Optional[Dict[str, Any]]:
        """Get random anime"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.JIKAN_API}/random/anime",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data")
        except Exception as e:
            logger.error(f"Jikan random error: {e}")
        return None

    # ========================================
    # KITSU API (FREE)
    # ========================================
    async def kitsu_search(
        self,
        query: str,
        media_type: str = "anime",  # anime, manga
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search on Kitsu"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.KITSU_API}/{media_type}",
                    params={
                        "filter[text]": query,
                        "page[limit]": limit,
                    },
                    headers={"Accept": "application/vnd.api+json"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Kitsu search error: {e}")
        return []

    async def kitsu_trending(
        self,
        media_type: str = "anime",
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get trending on Kitsu"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.KITSU_API}/trending/{media_type}",
                    params={"page[limit]": limit},
                    headers={"Accept": "application/vnd.api+json"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", [])
        except Exception as e:
            logger.error(f"Kitsu trending error: {e}")
        return []

    # ========================================
    # ANILIST GraphQL API
    # ========================================
    async def anilist_search(
        self,
        query: str,
        media_type: str = "ANIME",  # ANIME, MANGA
        per_page: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search on AniList"""
        graphql_query = """
        query ($search: String, $type: MediaType, $perPage: Int) {
            Page(perPage: $perPage) {
                media(search: $search, type: $type) {
                    id
                    title { romaji english native }
                    description
                    episodes
                    chapters
                    status
                    averageScore
                    genres
                    coverImage { large medium }
                    bannerImage
                    startDate { year month day }
                    endDate { year month day }
                }
            }
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ANILIST_API,
                    json={
                        "query": graphql_query,
                        "variables": {
                            "search": query,
                            "type": media_type,
                            "perPage": per_page,
                        },
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            logger.error(f"AniList search error: {e}")
        return []

    async def anilist_trending(
        self,
        media_type: str = "ANIME",
        per_page: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get trending on AniList"""
        graphql_query = """
        query ($type: MediaType, $perPage: Int) {
            Page(perPage: $perPage) {
                media(type: $type, sort: TRENDING_DESC) {
                    id
                    title { romaji english }
                    episodes
                    averageScore
                    genres
                    coverImage { large }
                    status
                }
            }
        }
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ANILIST_API,
                    json={
                        "query": graphql_query,
                        "variables": {"type": media_type, "perPage": per_page},
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            logger.error(f"AniList trending error: {e}")
        return []

    # ========================================
    # UNIFIED METHODS
    # ========================================
    async def get_recommendations(
        self,
        genre: Optional[str] = None,
        source: str = "jikan",
    ) -> List[Dict[str, Any]]:
        """Get anime recommendations"""
        if source == "jikan":
            return await self.jikan_top_anime("bypopularity")
        elif source == "kitsu":
            return await self.kitsu_trending()
        elif source == "anilist":
            return await self.anilist_trending()
        return []

    async def search_all(
        self,
        query: str,
        media_type: str = "anime",
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all sources"""
        results = {}

        if media_type == "anime":
            jikan_results = await self.jikan_search_anime(query)
            results["jikan"] = jikan_results.get("data", [])
            results["kitsu"] = await self.kitsu_search(query, "anime")
            results["anilist"] = await self.anilist_search(query, "ANIME")
        else:
            jikan_results = await self.jikan_search_manga(query)
            results["jikan"] = jikan_results.get("data", [])
            results["kitsu"] = await self.kitsu_search(query, "manga")
            results["anilist"] = await self.anilist_search(query, "MANGA")

        return results
