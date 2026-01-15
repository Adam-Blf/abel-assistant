"""
A.B.E.L - News Service
Integrates NewsAPI, HackerNews, Reddit, RSS
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from app.core.logging import logger


class NewsService:
    """
    News service integrating:
    - NewsAPI.org
    - Hacker News
    - Reddit
    - GNews
    """

    NEWSAPI_URL = "https://newsapi.org/v2"
    HACKERNEWS_URL = "https://hacker-news.firebaseio.com/v0"
    REDDIT_URL = "https://www.reddit.com"
    GNEWS_URL = "https://gnews.io/api/v4"

    def __init__(self):
        self.newsapi_key = getattr(settings, 'news_api_key', '')
        self.gnews_key = getattr(settings, 'gnews_api_key', '')

    # ========================================
    # NEWS API
    # ========================================
    async def newsapi_headlines(
        self,
        country: str = "fr",
        category: Optional[str] = None,  # business, entertainment, general, health, science, sports, technology
        q: Optional[str] = None,
        page_size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get top headlines from NewsAPI"""
        try:
            params = {
                "apiKey": self.newsapi_key,
                "country": country,
                "pageSize": page_size,
            }
            if category:
                params["category"] = category
            if q:
                params["q"] = q

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.NEWSAPI_URL}/top-headlines",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("articles", [])
        except Exception as e:
            logger.error(f"NewsAPI headlines error: {e}")
        return []

    async def newsapi_search(
        self,
        q: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        sort_by: str = "publishedAt",  # relevancy, popularity, publishedAt
        page_size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Search news articles"""
        try:
            params = {
                "apiKey": self.newsapi_key,
                "q": q,
                "sortBy": sort_by,
                "pageSize": page_size,
                "language": "fr",
            }
            if from_date:
                params["from"] = from_date
            if to_date:
                params["to"] = to_date

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.NEWSAPI_URL}/everything",
                    params=params,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("articles", [])
        except Exception as e:
            logger.error(f"NewsAPI search error: {e}")
        return []

    # ========================================
    # HACKER NEWS (FREE - No auth)
    # ========================================
    async def hackernews_top(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get top stories from Hacker News"""
        try:
            async with httpx.AsyncClient() as client:
                # Get top story IDs
                response = await client.get(
                    f"{self.HACKERNEWS_URL}/topstories.json",
                    timeout=10.0,
                )
                if response.status_code != 200:
                    return []

                story_ids = response.json()[:limit]

                # Fetch story details
                stories = []
                for story_id in story_ids:
                    story_response = await client.get(
                        f"{self.HACKERNEWS_URL}/item/{story_id}.json",
                        timeout=5.0,
                    )
                    if story_response.status_code == 200:
                        stories.append(story_response.json())

                return stories
        except Exception as e:
            logger.error(f"HackerNews error: {e}")
        return []

    async def hackernews_new(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get new stories from Hacker News"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.HACKERNEWS_URL}/newstories.json",
                    timeout=10.0,
                )
                if response.status_code != 200:
                    return []

                story_ids = response.json()[:limit]
                stories = []

                for story_id in story_ids:
                    story_response = await client.get(
                        f"{self.HACKERNEWS_URL}/item/{story_id}.json",
                        timeout=5.0,
                    )
                    if story_response.status_code == 200:
                        stories.append(story_response.json())

                return stories
        except Exception as e:
            logger.error(f"HackerNews new error: {e}")
        return []

    async def hackernews_best(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get best stories from Hacker News"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.HACKERNEWS_URL}/beststories.json",
                    timeout=10.0,
                )
                if response.status_code != 200:
                    return []

                story_ids = response.json()[:limit]
                stories = []

                for story_id in story_ids:
                    story_response = await client.get(
                        f"{self.HACKERNEWS_URL}/item/{story_id}.json",
                        timeout=5.0,
                    )
                    if story_response.status_code == 200:
                        stories.append(story_response.json())

                return stories
        except Exception as e:
            logger.error(f"HackerNews best error: {e}")
        return []

    # ========================================
    # REDDIT (FREE - No auth for public)
    # ========================================
    async def reddit_subreddit(
        self,
        subreddit: str,
        sort: str = "hot",  # hot, new, top, rising
        limit: int = 25,
        time: str = "day",  # hour, day, week, month, year, all (for top)
    ) -> List[Dict[str, Any]]:
        """Get posts from a subreddit"""
        try:
            params = {"limit": limit}
            if sort == "top":
                params["t"] = time

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.REDDIT_URL}/r/{subreddit}/{sort}.json",
                    params=params,
                    headers={"User-Agent": "ABEL/1.0"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    return [post["data"] for post in posts]
        except Exception as e:
            logger.error(f"Reddit error: {e}")
        return []

    async def reddit_search(
        self,
        query: str,
        subreddit: Optional[str] = None,
        sort: str = "relevance",
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Search Reddit"""
        try:
            url = f"{self.REDDIT_URL}/search.json"
            if subreddit:
                url = f"{self.REDDIT_URL}/r/{subreddit}/search.json"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params={
                        "q": query,
                        "sort": sort,
                        "limit": limit,
                        "restrict_sr": "1" if subreddit else "0",
                    },
                    headers={"User-Agent": "ABEL/1.0"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    return [post["data"] for post in posts]
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
        return []

    # ========================================
    # AGGREGATED NEWS
    # ========================================
    async def get_tech_news(self, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """Get tech news from multiple sources"""
        return {
            "newsapi": await self.newsapi_headlines(category="technology", page_size=limit),
            "hackernews": await self.hackernews_top(limit),
            "reddit": await self.reddit_subreddit("technology", limit=limit),
        }

    async def get_trending(self, country: str = "fr") -> List[Dict[str, Any]]:
        """Get trending news"""
        return await self.newsapi_headlines(country=country, page_size=20)

    async def search_all(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Search news across all sources"""
        return {
            "newsapi": await self.newsapi_search(query),
            "reddit": await self.reddit_search(query),
        }

    # Tech subreddits
    TECH_SUBREDDITS = [
        "technology", "programming", "webdev", "python",
        "javascript", "rust", "golang", "machinelearning",
        "artificial", "datascience", "cybersecurity",
        "linux", "apple", "android", "gaming",
    ]

    # News categories
    NEWS_CATEGORIES = [
        "business", "entertainment", "general",
        "health", "science", "sports", "technology",
    ]
