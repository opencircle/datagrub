"""
Redis client for caching and pub/sub
"""
import redis.asyncio as redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisClient:
    """Async Redis client wrapper"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

    async def connect(self):
        """Establish Redis connection"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        self.pubsub = self.redis.pubsub()

    async def disconnect(self):
        """Close Redis connection"""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

    # Cache Operations
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis:
            return None
        return await self.redis.get(key)

    async def set(
        self, key: str, value: Any, ttl: int = settings.REDIS_CACHE_TTL
    ) -> bool:
        """Set value in cache with TTL"""
        if not self.redis:
            return False

        if isinstance(value, (dict, list)):
            value = json.dumps(value)

        return await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis:
            return False
        return await self.redis.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        return await self.redis.exists(key) > 0

    # Pub/Sub Operations
    async def publish(self, channel: str, message: dict) -> int:
        """Publish message to channel"""
        if not self.redis:
            return 0
        return await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, *channels: str):
        """Subscribe to channels"""
        if self.pubsub:
            await self.pubsub.subscribe(*channels)

    async def unsubscribe(self, *channels: str):
        """Unsubscribe from channels"""
        if self.pubsub:
            await self.pubsub.unsubscribe(*channels)

    async def get_message(self):
        """Get message from subscribed channels"""
        if self.pubsub:
            return await self.pubsub.get_message()
        return None

    # List Operations
    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to list (left)"""
        if not self.redis:
            return 0
        json_values = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return await self.redis.lpush(key, *json_values)

    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to list (right)"""
        if not self.redis:
            return 0
        json_values = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in values]
        return await self.redis.rpush(key, *json_values)

    async def lrange(self, key: str, start: int = 0, end: int = -1) -> list:
        """Get range from list"""
        if not self.redis:
            return []
        values = await self.redis.lrange(key, start, end)
        return [json.loads(v) if v.startswith(("{", "[")) else v for v in values]


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency for getting Redis client"""
    return redis_client
