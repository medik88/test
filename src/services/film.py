import logging
import uuid
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import exceptions as es_exceptions
from fastapi import Depends

from core import config
from core.exceptions import NotFoundError
from db.elastic import WrappedAsyncElasticsearch, get_elastic
from db.redis import get_redis
from models.film import Film

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: WrappedAsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_page(
        self,
        page_number: int = 1,
        page_size: int = None,
        sort: str = None,
        genre_id: uuid.UUID = None,
    ) -> list[Film]:
        body = {"query": {"bool": {"must": [{"match_all": {}}]}}}

        if sort is not None:
            body["sort"] = self._get_sorting(sort)

        if genre_id is not None:
            body["query"]["bool"]["filter"] = [{"term": {"genres_ids": genre_id}}]

        try:
            resp = await self.elastic.search(
                index=config.ELASTIC_MOVIES_INDEX,
                body=body,
                size=page_size,
                from_=(page_number - 1) * page_size,
            )
        except es_exceptions.NotFoundError as e:
            raise NotFoundError

        try:
            return [Film(uuid=f["_id"], **f["_source"]) for f in resp["hits"]["hits"]]
        except KeyError:
            logger.error("Something wrong happened")
            return []

    @staticmethod
    def _get_sorting(sort: str) -> dict[str, dict[str, str]]:
        if sort.startswith("-"):
            sort_field = sort[1:]
            order = "desc"
        else:
            sort_field = sort
            order = "asc"

        if sort_field == "title":
            sort_field = "title.raw"

        return {sort_field: {"order": order}}

    async def search(
        self, query: str, page_number: int = 1, page_size: int = None
    ) -> Optional[list[Film]]:
        try:
            resp = await self.elastic.search(
                index=config.ELASTIC_MOVIES_INDEX,
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": [
                                "title",
                                "description",
                                "actors_names",
                                "directors_names",
                                "writers_names",
                            ],
                        }
                    },
                    "sort": {"imdb_rating": {"order": "desc"}},
                },
                size=page_size,
                from_=(page_number - 1) * page_size,
            )
        except es_exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        try:
            return [Film(uuid=f["_id"], **f["_source"]) for f in resp["hits"]["hits"]]
        except KeyError:
            logger.error("Something wrong happened")
            return None

    async def get_by_id(self, film_id: uuid.UUID) -> Optional[Film]:
        try:
            doc = await self.elastic.get(config.ELASTIC_MOVIES_INDEX, film_id)
        except es_exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        film = Film(**doc["_source"], uuid=doc["_id"])
        return film


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: WrappedAsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
