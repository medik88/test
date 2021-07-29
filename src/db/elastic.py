from elasticsearch import AsyncElasticsearch

from db.redis import redis_cache


class WrappedAsyncElasticsearch(AsyncElasticsearch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @redis_cache
    async def get(self, *args, **kwargs):
        return await super().get(*args, **kwargs)

    @redis_cache
    async def search(self, *args, **kwargs):
        return await super().search(*args, **kwargs)



async def get_elastic() -> WrappedAsyncElasticsearch:
    return es

es: WrappedAsyncElasticsearch = None
