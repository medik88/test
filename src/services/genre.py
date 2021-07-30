from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import elasticsearch
from aioredis import Redis
from fastapi import Depends

from core import config
from db.elastic import WrappedAsyncElasticsearch, get_elastic
from db.redis import get_redis
from models.film import Genre


class GenreService:
    def __init__(self, redis: Redis, elastic: WrappedAsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(config.ELASTIC_GENRES_INDEX, str(genre_id))
        except elasticsearch.exceptions.NotFoundError:
            return None
        return Genre(**doc['_source'], uuid=doc['_id'])

    async def get_all(self) -> List[Genre]:
        result = await self.elastic.search(index=config.ELASTIC_GENRES_INDEX, body={"query": {"match_all": {}}})
        return [Genre(**doc['_source'], uuid=doc['_id']) for doc in result['hits']['hits']]


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: WrappedAsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
