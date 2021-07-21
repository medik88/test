import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from api.v1.film import BaseFilm
from services.person import PersonService, get_person_service

router = APIRouter()

logger = logging.getLogger(__name__)


class Person(BaseModel):
    uuid: UUID
    full_name: str
    role: str
    film_ids: List[UUID]


@router.get('/{uuid}', response_model=Person)
async def person_details(uuid: UUID, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return Person(uuid=person.uuid, full_name=person.name, role=person.role, film_ids=person.film_ids)


@router.get('/{uuid}/film', response_model=List[BaseFilm])
async def films_by_person(uuid, person_service: PersonService = Depends(get_person_service)) -> List[BaseFilm]:
    films = await person_service.get_films_for_person(uuid)
    return [BaseFilm(uuid=film.uuid, title=film.title, imdb_rating=film.imdb_rating) for film in films]


@router.get('/search/', response_model=List[Person])
async def person_search_list(
        query: str = Query(..., min_length=2),
        page_number: int = Query(..., alias='page[number]', ge=1),
        page_size: int = Query(..., alias='page[size]', ge=1),
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    persons = await person_service.search_persons(query, page_number, page_size)
    return [Person(uuid=person.uuid, full_name=person.name, role=person.role, film_ids=person.film_ids) for person in
            persons]
