from uuid import UUID
from http import HTTPStatus
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service

router = APIRouter()


class BaseFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: float


class Film(BaseFilm):
    description: str
    genres: List[Dict[UUID, str]]
    actors: List[Dict[UUID, str]]
    writers: List[Dict[UUID, str]]
    directors: List[Dict[UUID, str]]


@router.get('/', response_model=List[BaseFilm])  #TODO
async def film_full_list() -> List[BaseFilm]:
    pass

@router.get('/{uuid}', response_model=Film)
async def film_details(uuid: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(uuid)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(uuid=film.uuid, title=film.title)  #TODO: полностью все поля должны заполняться

@router.get('/search', response_model=List[BaseFilm])  #TODO
async def film_search_list() -> List[BaseFilm]:
    pass
