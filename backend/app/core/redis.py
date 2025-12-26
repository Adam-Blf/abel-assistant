"""
A.B.E.L - Redis Configuration
"""

import json
from typing import Any, Optional
from redis import asyncio as aioredis

from app.core.config import settings
from app.core.logging import logger


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self._client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection."""
        try:
            self._client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return await self.client.get(key)

    async def set(
        self, key: str, value: Any, expire: Optional[int] = None
    ) -> bool:
        """Set a value in Redis with optional expiration."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        """Delete a key from Redis."""
        return await self.client.delete(key)

    async def get_json(self, key: str) -> Optional[dict]:
        """Get a JSON value from Redis."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    async def set_json(
        self, key: str, value: dict, expire: Optional[int] = None
    ) -> bool:
        """Set a JSON value in Redis."""
        return await self.set(key, json.dumps(value), expire)

    async def incr(self, key: str) -> int:
        """Increment a counter."""
        return await self.client.incr(key)

    async def publish(self, channel: str, message: str) -> int:
        """Publish a message to a channel."""
        return await self.client.publish(channel, message)


# Global Redis client instance
redis_client = RedisClient()
