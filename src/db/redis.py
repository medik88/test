from aioredis import Redis
from functools import wraps
from hashlib import sha1
import json

redis: Redis = None
CACHE_EXPIRE_IN_SECONDS = 60 * 5


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


def redis_cache(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        redis = await get_redis()
        kwd_mark = object()
        keys = ('prefix', fn.__name__,) + args + (kwd_mark,) + tuple(sorted(kwargs.items()))
        key = sha1(str(keys).encode()).hexdigest()
        data = await redis.get(key)
        if not data:
            result = await fn(*args, **kwargs)
            await redis.set(key, json.dumps(result), expire=CACHE_EXPIRE_IN_SECONDS)
        else:
            result = json.loads(data)
        return result

    return wrapper
