from functools import wraps
from hashlib import sha1

import orjson
from aioredis import Redis

from core.config import REDIS_CACHE_EXPIRE_S

redis: Redis = None


async def get_redis() -> Redis:
    return redis


def redis_cache(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        redis = await get_redis()
        keys = ('prefix', fn.__name__,) + args + tuple(sorted(kwargs.items()))
        key = sha1(str(keys).encode()).hexdigest()
        data = await redis.get(key)
        if not data:
            result = await fn(*args, **kwargs)
            await redis.set(key, orjson.dumps(result), expire=REDIS_CACHE_EXPIRE_S)
        else:
            result = orjson.loads(data)
        return result

    return wrapper
