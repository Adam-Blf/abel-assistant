"""
A.B.E.L - Complete API Registry
All 1400+ APIs from public-apis organized by category
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import httpx
from app.core.logging import logger


class APICategory(str, Enum):
    """All API categories from public-apis"""
    ANIMALS = "Animals"
    ANIME = "Anime"
    ANTI_MALWARE = "Anti-Malware"
    ART_DESIGN = "Art & Design"
    AUTHENTICATION = "Authentication"
    BLOCKCHAIN = "Blockchain"
    BOOKS = "Books"
    BUSINESS = "Business"
    CALENDAR = "Calendar"
    CLOUD_STORAGE = "Cloud Storage & File Sharing"
    CONTINUOUS_INTEGRATION = "Continuous Integration"
    CRYPTOCURRENCY = "Cryptocurrency"
    CURRENCY_EXCHANGE = "Currency Exchange"
    DATA_VALIDATION = "Data Validation"
    DEVELOPMENT = "Development"
    DICTIONARIES = "Dictionaries"
    DOCUMENTS = "Documents & Productivity"
    EMAIL = "Email"
    ENTERTAINMENT = "Entertainment"
    ENVIRONMENT = "Environment"
    EVENTS = "Events"
    FINANCE = "Finance"
    FOOD_DRINK = "Food & Drink"
    GAMES_COMICS = "Games & Comics"
    GEOCODING = "Geocoding"
    GOVERNMENT = "Government"
    HEALTH = "Health"
    JOBS = "Jobs"
    MACHINE_LEARNING = "Machine Learning"
    MUSIC = "Music"
    NEWS = "News"
    OPEN_DATA = "Open Data"
    OPEN_SOURCE = "Open Source Projects"
    PATENT = "Patent"
    PERSONALITY = "Personality"
    PHONE = "Phone"
    PHOTOGRAPHY = "Photography"
    PROGRAMMING = "Programming"
    SCIENCE_MATH = "Science & Math"
    SECURITY = "Security"
    SHOPPING = "Shopping"
    SOCIAL = "Social"
    SPORTS_FITNESS = "Sports & Fitness"
    TEST_DATA = "Test Data"
    TEXT_ANALYSIS = "Text Analysis"
    TRACKING = "Tracking"
    TRANSPORTATION = "Transportation"
    URL_SHORTENERS = "URL Shorteners"
    VEHICLE = "Vehicle"
    VIDEO = "Video"
    WEATHER = "Weather"


@dataclass
class APIEndpoint:
    """Represents a single API endpoint"""
    name: str
    description: str
    url: str
    category: str
    auth: str  # "", "apiKey", "OAuth", "X-Mashape-Key", etc.
    https: bool
    cors: str  # "yes", "no", "unknown"

    @property
    def is_free(self) -> bool:
        return self.auth in ["", "No"]

    @property
    def requires_key(self) -> bool:
        return self.auth.lower() in ["apikey", "x-mashape-key"]


class APIRegistry:
    """
    Complete registry of 1400+ public APIs
    Organized by category with search and filtering
    """

    PUBLIC_APIS_URL = "https://api.publicapis.org/entries"

    def __init__(self):
        self._apis: List[APIEndpoint] = []
        self._by_category: Dict[str, List[APIEndpoint]] = {}
        self._loaded = False

    async def load_all_apis(self) -> int:
        """Load all APIs from public-apis repository"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.PUBLIC_APIS_URL, timeout=30.0)
                if response.status_code == 200:
                    data = response.json()
                    entries = data.get("entries", [])

                    self._apis = []
                    self._by_category = {}

                    for entry in entries:
                        api = APIEndpoint(
                            name=entry.get("API", ""),
                            description=entry.get("Description", ""),
                            url=entry.get("Link", ""),
                            category=entry.get("Category", ""),
                            auth=entry.get("Auth", ""),
                            https=entry.get("HTTPS", False),
                            cors=entry.get("Cors", "unknown"),
                        )
                        self._apis.append(api)

                        if api.category not in self._by_category:
                            self._by_category[api.category] = []
                        self._by_category[api.category].append(api)

                    self._loaded = True
                    logger.info(f"Loaded {len(self._apis)} APIs in {len(self._by_category)} categories")
                    return len(self._apis)

        except Exception as e:
            logger.error(f"Failed to load APIs: {e}")
        return 0

    def get_all_apis(self) -> List[APIEndpoint]:
        """Get all loaded APIs"""
        return self._apis

    def get_by_category(self, category: str) -> List[APIEndpoint]:
        """Get APIs by category"""
        return self._by_category.get(category, [])

    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self._by_category.keys())

    def search(self, query: str, category: Optional[str] = None) -> List[APIEndpoint]:
        """Search APIs by name or description"""
        query_lower = query.lower()
        results = []

        apis = self._by_category.get(category, self._apis) if category else self._apis

        for api in apis:
            if query_lower in api.name.lower() or query_lower in api.description.lower():
                results.append(api)

        return results

    def get_free_apis(self, category: Optional[str] = None) -> List[APIEndpoint]:
        """Get APIs that don't require authentication"""
        apis = self._by_category.get(category, self._apis) if category else self._apis
        return [api for api in apis if api.is_free]

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            "total_apis": len(self._apis),
            "total_categories": len(self._by_category),
            "free_apis": len([a for a in self._apis if a.is_free]),
            "https_apis": len([a for a in self._apis if a.https]),
            "cors_enabled": len([a for a in self._apis if a.cors == "yes"]),
            "categories": {cat: len(apis) for cat, apis in self._by_category.items()},
        }


# Pre-configured popular APIs for quick access
FEATURED_APIS = {
    # Weather
    "openweathermap": {"url": "https://api.openweathermap.org/data/2.5", "category": "Weather"},
    "weatherapi": {"url": "https://api.weatherapi.com/v1", "category": "Weather"},

    # Finance
    "exchangerate": {"url": "https://api.exchangerate-api.com/v4", "category": "Currency Exchange"},
    "coinbase": {"url": "https://api.coinbase.com/v2", "category": "Cryptocurrency"},
    "coingecko": {"url": "https://api.coingecko.com/api/v3", "category": "Cryptocurrency"},
    "alpha_vantage": {"url": "https://www.alphavantage.co/query", "category": "Finance"},

    # News
    "newsapi": {"url": "https://newsapi.org/v2", "category": "News"},
    "hackernews": {"url": "https://hacker-news.firebaseio.com/v0", "category": "News"},

    # Entertainment
    "tmdb": {"url": "https://api.themoviedb.org/3", "category": "Video"},
    "spotify": {"url": "https://api.spotify.com/v1", "category": "Music"},
    "tvmaze": {"url": "https://api.tvmaze.com", "category": "Video"},
    "jikan": {"url": "https://api.jikan.moe/v4", "category": "Anime"},

    # Development
    "github": {"url": "https://api.github.com", "category": "Development"},
    "stackoverflow": {"url": "https://api.stackexchange.com/2.3", "category": "Development"},
    "npm": {"url": "https://registry.npmjs.org", "category": "Development"},
    "pypi": {"url": "https://pypi.org/pypi", "category": "Development"},

    # Data
    "restcountries": {"url": "https://restcountries.com/v3.1", "category": "Geocoding"},
    "ipapi": {"url": "https://ipapi.co", "category": "Geocoding"},
    "randomuser": {"url": "https://randomuser.me/api", "category": "Test Data"},

    # Fun
    "chucknorris": {"url": "https://api.chucknorris.io", "category": "Entertainment"},
    "catfacts": {"url": "https://catfact.ninja", "category": "Animals"},
    "dogapi": {"url": "https://dog.ceo/api", "category": "Animals"},
    "quotable": {"url": "https://api.quotable.io", "category": "Entertainment"},

    # Utilities
    "qrserver": {"url": "https://api.qrserver.com/v1", "category": "Data Validation"},
    "urlscan": {"url": "https://urlscan.io/api/v1", "category": "Security"},
}
