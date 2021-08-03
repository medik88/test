from elasticsearch import AsyncElasticsearch

from db.cache import cache_request


class WrappedAsyncElasticsearch(AsyncElasticsearch):

    @cache_request
    async def get(self, *args, **kwargs):
        return await super().get(*args, **kwargs)

    @cache_request
    async def search(self, *args, **kwargs):
        return await super().search(*args, **kwargs)


async def get_elastic() -> WrappedAsyncElasticsearch:
    return es


es: WrappedAsyncElasticsearch = None
