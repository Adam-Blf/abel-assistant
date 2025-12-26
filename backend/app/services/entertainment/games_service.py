"""
A.B.E.L - Games Service
Integrates RAWG, IGDB, Steam, CheapShark
"""

from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger


class GamesService:
    """
    Games service integrating:
    - RAWG (Video Games Database)
    - CheapShark (Game Deals)
    - Free-to-Game API
    - Steam Store API
    """

    RAWG_API = "https://api.rawg.io/api"
    CHEAPSHARK_API = "https://www.cheapshark.com/api/1.0"
    FREETOGAME_API = "https://www.freetogame.com/api"
    STEAM_API = "https://store.steampowered.com/api"

    def __init__(self):
        self.rawg_key = getattr(settings, 'rawg_api_key', '')

    # ========================================
    # RAWG API
    # ========================================
    async def rawg_search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """Search games on RAWG"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.RAWG_API}/games",
                    params={
                        "key": self.rawg_key,
                        "search": query,
                        "page": page,
                        "page_size": page_size,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"RAWG search error: {e}")
        return {"results": []}

    async def rawg_get_game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get game details from RAWG"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.RAWG_API}/games/{game_id}",
                    params={"key": self.rawg_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"RAWG game error: {e}")
        return None

    async def rawg_top_games(
        self,
        ordering: str = "-rating",  # -rating, -released, -added, -metacritic
        page: int = 1,
        page_size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top rated games"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.RAWG_API}/games",
                    params={
                        "key": self.rawg_key,
                        "ordering": ordering,
                        "page": page,
                        "page_size": page_size,
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG top games error: {e}")
        return []

    async def rawg_get_genres(self) -> List[Dict[str, Any]]:
        """Get all game genres"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.RAWG_API}/genres",
                    params={"key": self.rawg_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG genres error: {e}")
        return []

    async def rawg_get_platforms(self) -> List[Dict[str, Any]]:
        """Get all platforms"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.RAWG_API}/platforms",
                    params={"key": self.rawg_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception as e:
            logger.error(f"RAWG platforms error: {e}")
        return []

    # ========================================
    # CHEAPSHARK API (FREE - No auth)
    # ========================================
    async def cheapshark_deals(
        self,
        store_id: Optional[int] = None,
        page: int = 0,
        page_size: int = 20,
        sort_by: str = "Deal Rating",
    ) -> List[Dict[str, Any]]:
        """Get game deals from CheapShark"""
        try:
            params = {
                "pageNumber": page,
                "pageSize": page_size,
                "sortBy": sort_by,
            }
            if store_id:
                params["storeID"] = store_id

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CHEAPSHARK_API}/deals",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CheapShark deals error: {e}")
        return []

    async def cheapshark_search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search games with deals"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CHEAPSHARK_API}/games",
                    params={"title": query, "limit": limit},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CheapShark search error: {e}")
        return []

    async def cheapshark_stores(self) -> List[Dict[str, Any]]:
        """Get all game stores"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.CHEAPSHARK_API}/stores",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"CheapShark stores error: {e}")
        return []

    # ========================================
    # FREE-TO-GAME API (FREE - No auth)
    # ========================================
    async def freetogame_list(
        self,
        platform: str = "all",  # pc, browser, all
        category: Optional[str] = None,
        sort_by: str = "relevance",  # relevance, popularity, release-date, alphabetical
    ) -> List[Dict[str, Any]]:
        """Get free-to-play games"""
        try:
            params = {"platform": platform, "sort-by": sort_by}
            if category:
                params["category"] = category

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FREETOGAME_API}/games",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"FreeToGame error: {e}")
        return []

    async def freetogame_get_game(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Get free game details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.FREETOGAME_API}/game",
                    params={"id": game_id},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"FreeToGame game error: {e}")
        return None

    async def freetogame_categories(self) -> List[str]:
        """Get F2P game categories"""
        return [
            "mmorpg", "shooter", "strategy", "moba", "racing", "sports",
            "social", "sandbox", "open-world", "survival", "pvp", "pve",
            "pixel", "voxel", "zombie", "turn-based", "first-person",
            "third-Person", "top-down", "tank", "space", "sailing",
            "side-scroller", "superhero", "permadeath", "card", "battle-royale",
            "mmo", "mmofps", "mmotps", "3d", "2d", "anime", "fantasy",
            "sci-fi", "fighting", "action-rpg", "action", "military",
            "martial-arts", "flight", "low-spec", "tower-defense", "horror"
        ]

    # ========================================
    # STEAM API (Partial - No auth for some)
    # ========================================
    async def steam_featured(self) -> Dict[str, Any]:
        """Get Steam featured games"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.STEAM_API}/featured",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            logger.error(f"Steam featured error: {e}")
        return {}

    async def steam_app_details(self, app_id: int) -> Optional[Dict[str, Any]]:
        """Get Steam app details"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.STEAM_API}/appdetails",
                    params={"appids": app_id},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get(str(app_id), {}).get("data")
        except Exception as e:
            logger.error(f"Steam app details error: {e}")
        return None

    # ========================================
    # RECOMMENDATIONS
    # ========================================
    async def get_recommendations(
        self,
        genre: Optional[str] = None,
        platform: Optional[str] = None,
        free_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get game recommendations"""
        if free_only:
            category = genre.lower().replace(" ", "-") if genre else None
            return await self.freetogame_list(
                platform=platform or "all",
                category=category,
            )

        if genre:
            search_result = await self.rawg_search(genre)
            return search_result.get("results", [])

        return await self.rawg_top_games()

    async def get_deals(
        self,
        query: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get best game deals"""
        if query:
            return await self.cheapshark_search(query, limit)
        return await self.cheapshark_deals(page_size=limit)
