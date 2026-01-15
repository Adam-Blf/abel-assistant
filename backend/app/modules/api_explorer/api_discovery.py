"""
A.B.E.L - API Discovery Service
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

import httpx

from app.core.logging import logger


class ApiDiscovery:
    """
    Service for discovering public APIs from the public-apis repository.

    Features:
    - Fetch API list from public-apis
    - Search by category
    - Filter by features (auth, CORS, HTTPS)
    - Test API availability
    """

    PUBLIC_APIS_URL = "https://api.publicapis.org/entries"
    GITHUB_JSON_URL = "https://raw.githubusercontent.com/public-apis/public-apis/master/scripts/tests/test.json"

    CATEGORIES = [
        "Animals", "Anime", "Anti-Malware", "Art & Design", "Books",
        "Business", "Calendar", "Cloud Storage & File Sharing",
        "Continuous Integration", "Cryptocurrency", "Currency Exchange",
        "Data Validation", "Development", "Dictionaries", "Documents & Productivity",
        "Environment", "Events", "Finance", "Food & Drink", "Games & Comics",
        "Geocoding", "Government", "Health", "Jobs", "Machine Learning",
        "Music", "News", "Open Data", "Open Source Projects", "Patent",
        "Personality", "Phone", "Photography", "Science & Math", "Security",
        "Shopping", "Social", "Sports & Fitness", "Test Data", "Text Analysis",
        "Tracking", "Transportation", "URL Shorteners", "Vehicle", "Video",
        "Weather",
    ]

    def __init__(self):
        self.cached_apis: List[Dict[str, Any]] = []
        self.last_fetch: Optional[datetime] = None

    async def fetch_all_apis(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch all public APIs from the repository.

        Args:
            force_refresh: Force refresh even if cached

        Returns:
            List of API entries
        """
        # Use cache if available and fresh (less than 1 hour old)
        if (
            self.cached_apis
            and self.last_fetch
            and not force_refresh
            and (datetime.utcnow() - self.last_fetch).seconds < 3600
        ):
            return self.cached_apis

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.PUBLIC_APIS_URL, timeout=30.0)

                if response.status_code == 200:
                    data = response.json()
                    self.cached_apis = data.get("entries", [])
                    self.last_fetch = datetime.utcnow()

                    logger.info(f"Fetched {len(self.cached_apis)} public APIs")
                    return self.cached_apis

        except Exception as e:
            logger.error(f"Error fetching APIs: {e}")

        return self.cached_apis

    async def search_by_category(
        self,
        category: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search APIs by category.

        Args:
            category: Category name
            limit: Maximum results

        Returns:
            List of matching APIs
        """
        apis = await self.fetch_all_apis()

        matching = [
            api for api in apis
            if api.get("Category", "").lower() == category.lower()
        ]

        return matching[:limit]

    async def search_by_keyword(
        self,
        keyword: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search APIs by keyword in name or description.

        Args:
            keyword: Search keyword
            limit: Maximum results

        Returns:
            List of matching APIs
        """
        apis = await self.fetch_all_apis()
        keyword_lower = keyword.lower()

        matching = [
            api for api in apis
            if keyword_lower in api.get("API", "").lower()
            or keyword_lower in api.get("Description", "").lower()
        ]

        return matching[:limit]

    async def search_free_apis(
        self,
        category: Optional[str] = None,
        cors_required: bool = False,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Search for free APIs with optional filters.

        Args:
            category: Optional category filter
            cors_required: Only return CORS-enabled APIs
            limit: Maximum results

        Returns:
            List of matching free APIs
        """
        apis = await self.fetch_all_apis()

        matching = []
        for api in apis:
            # Check if free (no auth required)
            if api.get("Auth", "") not in ["", "No"]:
                continue

            # Check category
            if category and api.get("Category", "").lower() != category.lower():
                continue

            # Check CORS
            if cors_required and api.get("Cors", "") != "yes":
                continue

            matching.append(api)

            if len(matching) >= limit:
                break

        return matching

    async def test_api_availability(
        self,
        api_url: str,
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Test if an API is available and responding.

        Args:
            api_url: The API base URL
            timeout: Request timeout in seconds

        Returns:
            Test results with status and response time
        """
        try:
            start_time = datetime.utcnow()

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    api_url,
                    timeout=timeout,
                    follow_redirects=True,
                )

                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                return {
                    "url": api_url,
                    "available": response.status_code < 500,
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "tested_at": datetime.utcnow().isoformat(),
                }

        except httpx.TimeoutException:
            return {
                "url": api_url,
                "available": False,
                "error": "timeout",
                "tested_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "url": api_url,
                "available": False,
                "error": str(e),
                "tested_at": datetime.utcnow().isoformat(),
            }

    async def get_random_api(
        self,
        category: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a random API from the list.

        Args:
            category: Optional category filter

        Returns:
            Random API entry
        """
        import random

        apis = await self.fetch_all_apis()

        if category:
            apis = [a for a in apis if a.get("Category", "").lower() == category.lower()]

        if apis:
            return random.choice(apis)

        return None

    def get_categories(self) -> List[str]:
        """Get list of all available categories."""
        return self.CATEGORIES

    async def get_api_stats(self) -> Dict[str, Any]:
        """Get statistics about available APIs."""
        apis = await self.fetch_all_apis()

        # Count by category
        category_counts = {}
        auth_counts = {"free": 0, "apiKey": 0, "oauth": 0, "other": 0}
        cors_counts = {"yes": 0, "no": 0, "unknown": 0}

        for api in apis:
            # Category
            cat = api.get("Category", "Unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

            # Auth
            auth = api.get("Auth", "").lower()
            if auth in ["", "no"]:
                auth_counts["free"] += 1
            elif "apikey" in auth:
                auth_counts["apiKey"] += 1
            elif "oauth" in auth:
                auth_counts["oauth"] += 1
            else:
                auth_counts["other"] += 1

            # CORS
            cors = api.get("Cors", "").lower()
            if cors == "yes":
                cors_counts["yes"] += 1
            elif cors == "no":
                cors_counts["no"] += 1
            else:
                cors_counts["unknown"] += 1

        return {
            "total_apis": len(apis),
            "categories": category_counts,
            "auth_distribution": auth_counts,
            "cors_distribution": cors_counts,
            "last_updated": self.last_fetch.isoformat() if self.last_fetch else None,
        }
