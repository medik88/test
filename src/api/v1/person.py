import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core import config
from core.exceptions import NotFoundError
from models.film import FilmForPerson as ServiceFilmForPerson
from models.film import Person as ServicePerson
from services.person import PersonService, get_person_service

router = APIRouter()

logger = logging.getLogger(__name__)


class FilmForPerson(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float

    @staticmethod
    def from_service_model(other: ServiceFilmForPerson):
        film = FilmForPerson(
            uuid=other.uid,
            title=other.title,
            imdb_rating=other.imdb_rating,
        )
        return film


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: List[FilmForPerson]

    @staticmethod
    def from_service_model(other: ServicePerson):
        films = []
        if other.filmworks:
            films = [FilmForPerson.from_service_model(filmwork) for filmwork in other.filmworks]
        person = Person(
            uuid=other.uuid,
            full_name=other.name,
            films=films
        )
        return person


@router.get(
    '/search',
    response_model=List[Person],
    summary="Поиск персон",
    description="Полнотекстовый поиск по персонам",
    response_description="Имя и работы персоны",
    tags=['Полнотекстовый поиск']
)
async def person_search_list(
        query: str = Query(..., min_length=2),
        page_number: int = Query(1, alias='page[number]', ge=1),
        page_size: int = Query(config.PAGE_SIZE, alias='page[size]', ge=1),
        person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    try:
        persons = await person_service.search_persons(query, page_number, page_size)
    except NotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.error)

    return [Person.from_service_model(person) for person in persons]


@router.get(
    '/{uuid}',
    response_model=Person,
    summary="Информация по персоне",
    description="Полная информация по персоне по её ID",
    response_description="Имя и работы персоны"
)
async def person_details(
        uuid: UUID,
        person_service: PersonService = Depends(get_person_service)
) -> Person:
    try:
        person = await person_service.get_by_id(uuid)
    except NotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.error)

    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person.from_service_model(person)


@router.get(
    '/{uuid}/film',
    response_model=List[FilmForPerson],
    summary="Работы персоны",
    description="Список работ персоны по её ID",
    response_description="Название и рейтинг фильма"
)
async def films_by_person(
        uuid: UUID,
        person_service: PersonService = Depends(get_person_service)
) -> List[FilmForPerson]:
    try:
        films = await person_service.get_films_for_person(uuid)
    except NotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.error)

    if films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return [FilmForPerson.from_service_model(film) for film in films]
