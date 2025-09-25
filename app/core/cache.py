import redis.asyncio as redis
import json
from typing import Any, Optional
import pickle
import asyncio

class CacheManager:
    def __init__(self):
        self.redis_client = None
    
    async def init_redis(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20
        )
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            if not self.redis_client:
                await self.init_redis()
            
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, expire: int = None):
        try:
            if not self.redis_client:
                await self.init_redis()
            
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.set(
                key, 
                serialized_value, 
                ex=expire or settings.CACHE_EXPIRE_SECONDS
            )
        except Exception:
            pass  # Fail silently for cache operations
    
    async def delete(self, key: str):
        try:
            if not self.redis_client:
                await self.init_redis()
            await self.redis_client.delete(key)
        except Exception:
            pass

cache = CacheManager()
