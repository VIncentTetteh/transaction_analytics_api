import aioredis
import json
from datetime import datetime
from app.core.config import settings

class Cache:
    def __init__(self):
        # Initialize the Redis connection with password
        self.REDIS_URL = settings.REDIS_URL
        
        redis_password = settings.REDIS_PASSWORD
        self.redis = aioredis.from_url(self.REDIS_URL, password=redis_password, decode_responses=True)

    async def set_cache(self, key, value, expire=None):
        # Convert datetime fields to ISO format strings before JSON encoding
        value = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in value.items()}
        await self.redis.set(key, json.dumps(value), ex=expire)

    async def get_cache(self, key: str) -> dict:
        """
        Gets a cache entry.
        :param key: The key of the cache entry.
        :return: The cached value as a dictionary, or None if not found.
        """
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def clear_cache(self, key: str) -> None:
        """
        Clears a specific cache entry.
        :param key: The key of the cache entry to clear.
        """
        await self.redis.delete(key)

    async def clear_all_cache(self) -> None:
        """
        Clears all cache entries.
        Use this carefully as it will flush the entire Redis database.
        """
        await self.redis.flushdb()

# Singleton instance of Cache for usage across the application
cache = Cache()
