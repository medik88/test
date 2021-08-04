from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

import elasticsearch
from fastapi import Depends

from core import config
from core.exceptions import NotFoundError
from db.elastic import WrappedAsyncElasticsearch, get_elastic
from models.film import FilmForPerson, Person


class AbstractPersonService(ABC):
    @abstractmethod
    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        pass

    @abstractmethod
    async def get_films_for_person(self, person_id: UUID) -> List[FilmForPerson]:
        pass

    @abstractmethod
    async def search_persons(self, query: str, page_number: int, page_size: int) -> List[Person]:
        pass


class PersonService(AbstractPersonService):
    def __init__(self, elastic: WrappedAsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        return await self._get_person_from_elastic(person_id)

    async def get_films_for_person(self, person_id: UUID) -> List[FilmForPerson]:
        person = await self._get_person_from_elastic(person_id)
        return person.filmworks if person else None

    async def search_persons(self, query: str, page_number: int, page_size: int) -> List[Person]:
        size = page_size
        offset = (page_number - 1) * page_size
        try:
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
        except elasticsearch.exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        persons = [Person(**item['_source'], uuid=item['_id']) for item in result['hits']['hits']]
        return persons

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(config.ELASTIC_PERSONS_INDEX, str(person_id))
        except elasticsearch.exceptions.NotFoundError as e:
            raise NotFoundError(e.error)

        return Person(**doc['_source'], uuid=doc['_id'])


@lru_cache()
def get_person_service(
        elastic: WrappedAsyncElasticsearch = Depends(get_elastic),
) -> AbstractPersonService:
    return PersonService(elastic)
