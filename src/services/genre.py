from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import elasticsearch
from fastapi import Depends

from core import config
from core.exceptions import NotFoundError
from db.elastic import WrappedAsyncElasticsearch, get_elastic
from models.film import Genre


class AbstractGenreService(ABC):
    @abstractmethod
    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        pass

    @abstractmethod
    async def get_all(self) -> List[Genre]:
        pass


class GenreService(AbstractGenreService):
    def __init__(self, elastic: WrappedAsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(config.ELASTIC_GENRES_INDEX, str(genre_id))
        except elasticsearch.exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        return Genre(**doc['_source'], uuid=doc['_id'])

    async def get_all(self) -> List[Genre]:
        try:
            result = await self.elastic.search(index=config.ELASTIC_GENRES_INDEX, body={"query": {"match_all": {}}})
        except elasticsearch.exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        return [Genre(**doc['_source'], uuid=doc['_id']) for doc in result['hits']['hits']]


@lru_cache()
def get_genre_service(
        elastic: WrappedAsyncElasticsearch = Depends(get_elastic),
) -> AbstractGenreService:
    return GenreService(elastic)
