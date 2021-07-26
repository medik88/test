import uuid
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as es_exceptions
from fastapi import Depends

from core import config
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_page(
            self,
            page_number: int = 1,
            page_size: int = None,
            sort: str = None,
            genre_id: uuid.UUID = None,
    ) -> list[Film]:
        body = {
            "query": {
                "bool": {
                    "must": [
                        {"match_all": {}}
                    ]
                }
            }
        }

        if sort is not None:
            body["sort"] = self.get_sorting(sort)

        if genre_id is not None:
            body["query"]["bool"]["filter"] = [{"term": {
                "genres_ids": genre_id
            }}]

        resp = await self.elastic.search(
            index=config.ELASTIC_MOVIES_INDEX,
            body=body,
            size=page_size,
            from_=page_number * page_size,
        )
        try:
            return [Film(uuid=f["_id"], **f["_source"]) for f in resp["hits"]["hits"]]
        except KeyError:
            return []

    def get_sorting(self, sort):
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
    ) -> list[Film]:
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
            from_=page_number * page_size,
        )
        try:
            return [Film(uuid=f["_id"], **f["_source"]) for f in resp["hits"]["hits"]]
        except KeyError:
            return []

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(config.ELASTIC_MOVIES_INDEX, film_id)
        except es_exceptions.NotFoundError:
            return None
        else:
            return Film(**doc["_source"], uuid=doc["_id"])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            str(film.uuid), film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
