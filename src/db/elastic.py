from elasticsearch import AsyncElasticsearch

from db.redis import redis_cache


async def WrappedAsyncElasticsearch(AsyncElasticsearch):
    @redis_cache
    def get(self, *args, **kwargs):
        super().get(args, kwargs)

    @redis_cache
    def search(self, *args, **kwargs):
        super().get(args, kwargs)


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> WrappedAsyncElasticsearch:
    return es
    

es: WrappedAsyncElasticsearch = None
