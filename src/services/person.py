from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import elasticsearch
from aioredis import Redis
from fastapi import Depends

from core import config
from db.elastic import WrappedAsyncElasticsearch, get_elastic
from db.redis import get_redis
from models.film import FilmForPerson, Person


class PersonService:
    def __init__(self, redis: Redis, elastic: WrappedAsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        return await self._get_person_from_elastic(person_id)

    async def get_films_for_person(self, person_id: UUID) -> List[FilmForPerson]:
        person = await self._get_person_from_elastic(person_id)
        return person.filmworks if person else None

    async def search_persons(self, query: str, page_number: int, page_size: int) -> List[Person]:
        size = page_size
        offset = (page_number - 1) * page_size
        result = await self.elastic.search(
            index=config.ELASTIC_PERSONS_INDEX,
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
        persons = [Person(**item['_source'], uuid=item['_id']) for item in result['hits']['hits']]
        return persons

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(config.ELASTIC_PERSONS_INDEX, str(person_id))
        except elasticsearch.exceptions.NotFoundError:
            return None
        return Person(**doc['_source'], uuid=doc['_id'])


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: WrappedAsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
