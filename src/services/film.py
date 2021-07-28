import uuid
import json
from functools import lru_cache
from typing import Optional
from functools import wraps
from hashlib import sha1

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch import exceptions as es_exceptions
from fastapi import Depends

from core import config
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

CACHE_EXPIRE_IN_SECONDS = 60 * 5


def cache_decorator(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        redis = await get_redis()
        kwd_mark = object()
        keys = args + (kwd_mark,) + tuple(sorted(kwargs.items()))
        key = sha1(str(keys).encode()).hexdigest()
        data = await redis.get(key)
        if not data:
            result = await fn(*args, **kwargs)
            await redis.set(key, json.dumps(result), expire=CACHE_EXPIRE_IN_SECONDS)
        else:
            result = json.loads(data)
        return result

    return wrapper


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
            'query': {
                'bool': {
                    'must': [
                        {'match_all': {}}
                    ]
                }
            }
        }

        if sort is not None:
            body['sort'] = self._get_sorting(sort)

        if genre_id is not None:
            body['query']['bool']['filter'] = [{'term': {
                'genres_ids': genre_id
            }}]

        resp = await self.elastic.search(
            index=config.ELASTIC_MOVIES_INDEX,
            body=body,
            size=page_size,
            from_=page_number * page_size,
        )
        try:
            return [Film(uuid=f['_id'], **f['_source']) for f in resp['hits']['hits']]
        except KeyError:
            return []

    @staticmethod
    def _get_sorting(sort: str) -> dict[str, dict[str, str]]:
        if sort.startswith('-'):
            sort_field = sort[1:]
            order = 'desc'
        else:
            sort_field = sort
            order = 'asc'

        if sort_field == 'title':
            sort_field = 'title.raw'

        return {sort_field: {'order': order}}

    async def search(
            self, query: str, page_number: int = 1, page_size: int = None
    ) -> list[Film]:
        resp = await self.elastic.search(
            index=config.ELASTIC_MOVIES_INDEX,
            body={
                'query': {
                    'multi_match': {
                        'query': query,
                        'fields': [
                            'title',
                            'description',
                            'actors_names',
                            'directors_names',
                            'writers_names',
                        ],
                    }
                },
                'sort': {'imdb_rating': {'order': 'desc'}},
            },
            size=page_size,
            from_=page_number * page_size,
        )
        try:
            return [Film(uuid=f['_id'], **f['_source']) for f in resp['hits']['hits']]
        except KeyError:
            return []

    @cache_decorator
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(config.ELASTIC_MOVIES_INDEX, film_id)
        except es_exceptions.NotFoundError:
            return None
        film = Film(**doc['_source'], uuid=doc['_id'])
        return film
            

@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
