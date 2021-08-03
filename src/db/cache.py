from abc import ABC, abstractmethod
from functools import wraps
from hashlib import sha1

import orjson
from aioredis import Redis

from core.config import REDIS_CACHE_EXPIRE_S


class AbstractCache(ABC):
    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def set(self, key, value, expire):
        pass


class RedisCache(AbstractCache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key):
        return await self.redis.get(key)

    async def set(self, key, value, expire):
        await self.redis.set(key, value, expire=expire)


redis_instance: Redis = None
redis_cache_instance: RedisCache = None


async def get_cache() -> AbstractCache:
    return redis_cache_instance


def cache_request(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        cache = await get_cache()
        keys = ('prefix', fn.__name__,) + args + tuple(sorted(kwargs.items()))
        key = sha1(str(keys).encode()).hexdigest()
        data = await cache.get(key)
        if not data:
            result = await fn(*args, **kwargs)
            await cache.set(key, orjson.dumps(result), expire=REDIS_CACHE_EXPIRE_S)
        else:
            result = orjson.loads(data)
        return result

    return wrapper
