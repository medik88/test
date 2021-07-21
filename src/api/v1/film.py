from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

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
        page_number: int = Query(..., alias='page[number]', ge=1),
        page_size: int = Query(..., alias='page[size]', ge=1)
) -> List[BaseFilm]:
    # todo add implementation
    pass

@router.get('/', response_model=List[BaseFilm])
async def film_full_list() -> List[BaseFilm]:
    # todo add implementation
    pass


@router.get('/{uuid}', response_model=Film)
async def film_details(uuid: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film.from_service_model(film)


