import typing
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from core import config
from core.exceptions import NoIndexError
from models.film import Film as ServiceFilm
from services.film import FilmService, get_film_service

router = APIRouter()


class BaseFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float

    @staticmethod
    def from_service_model(other: ServiceFilm):
        film = BaseFilm(
            uuid=other.uuid,
            title=other.title,
            imdb_rating=other.imdb_rating,
        )
        return film


class PersonShort(BaseModel):
    uid: UUID
    name: str


class GenreShort(BaseModel):
    uid: UUID
    name: str


class Film(BaseFilm):
    description: str
    genres: List[GenreShort]
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

    @staticmethod
    def from_service_model(other: ServiceFilm):
        film = Film(
            uuid=other.uuid,
            title=other.title,
            imdb_rating=other.imdb_rating,
            description=other.description,
            genres=other.genres,
            actors=other.actors,
            writers=other.writers,
            directors=other.directors
        )
        return film


@router.get('/search', response_model=List[BaseFilm])
async def film_search_list(
        query: str = Query(..., min_length=2),
        page_number: typing.Optional[int] = Query(1, alias='page[number]', ge=1),
        page_size: typing.Optional[int] = Query(config.PAGE_SIZE, alias='page[size]', ge=1),
        film_service: FilmService = Depends(get_film_service)
) -> List[BaseFilm]:
    try:
        model_films = await film_service.search(query, page_number, page_size)
    except NoIndexError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='index not found')

    if model_films is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='filmworks not found')

    if model_films:
        return [BaseFilm(uuid=f.uuid, title=f.title, imdb_rating=f.imdb_rating) for f in model_films]

    return []


@router.get('/', response_model=List[BaseFilm])
async def film_full_list(
        page_number: typing.Optional[int] = Query(1, alias='page[number]', ge=1),
        page_size: typing.Optional[int] = Query(config.PAGE_SIZE, alias='page[size]', ge=1),
        sort: str = Query(None, regex='^-?(?:title|imdb_rating)$'),
        genre_id: UUID = Query(None, alias='filter[genre]'),
        film_service: FilmService = Depends(get_film_service)
) -> List[BaseFilm]:
    model_films = await film_service.get_page(page_number, page_size, sort, genre_id)
    if model_films:
        return [BaseFilm(uuid=f.uuid, title=f.title, imdb_rating=f.imdb_rating) for f in model_films]
    return []


@router.get('/{uuid}', response_model=Film)
async def film_details(uuid: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='filmwork not found')
    return Film.from_service_model(film)
