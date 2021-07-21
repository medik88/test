from functools import lru_cache
from typing import Optional, List

import elasticsearch
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Person, Film


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index_name = 'persons'
        self.movies_index_name = 'movies'

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(self.index_name, person_id)
        except elasticsearch.exceptions.NotFoundError:
            return None
        person = Person(**doc['_source'], uuid=doc['_id'], role='', film_ids=[])
        films_for_person = await self._get_films_for_person_from_elastic(person_id)
        person.film_ids = [film.uuid for film in films_for_person]
        return person

    async def get_films_for_person(self, person_id: str) -> List[Film]:
        return await self._get_films_for_person_from_elastic(person_id)

    async def search_persons(self, query: str, page_number: int, page_size: int) -> List[Film]:
        size = page_size
        offset = (page_number - 1) * page_size
        result = await self.elastic.search(
            index=self.index_name,
            body={
                "from": offset,
                "size": size,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fuzziness": "auto",
                        "fields": [
                            "name"
                        ]
                    }
                }
            }
        )

        persons = [Person(**doc['_source'], uuid=doc['_id'], role='', film_ids=[]) for doc in result['hits']['hits']]
        return persons

    async def _get_films_for_person_from_elastic(self, person_uuid) -> List[Film]:
        try:
            result = await self.elastic.search(
                index=self.movies_index_name,
                body={
                    "query": {
                        "bool": {
                            "should": [

                                {
                                    "nested": {
                                        "path": "actors",
                                        "query": {
                                            "bool": {
                                                "filter": [
                                                    {"term": {"actors.uid": person_uuid}}
                                                ]
                                            }

                                        }
                                    }
                                },
                                {"nested": {
                                    "path": "writers",
                                    "query": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"writers.uid": person_uuid}}
                                            ]
                                        }

                                    }
                                }},
                                {"nested": {
                                    "path": "directors",
                                    "query": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"directors.uid": person_uuid}}
                                            ]
                                        }

                                    }
                                }}
                            ]
                        }
                    }
                }
            )
        except elasticsearch.exceptions.NotFoundError:
            return []
        return [Film(**doc['_source'], uuid=doc['_id']) for doc in result['hits']['hits']]


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
