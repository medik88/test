from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.exceptions import NotFoundError
from services.genre import AbstractGenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    uuid: UUID
    name: str


@router.get('/{uuid}', response_model=Genre)
async def genre_details(uuid: UUID, genre_service: AbstractGenreService = Depends(get_genre_service)) -> Genre:
    try:
        genre = await genre_service.get_by_id(uuid)
    except NotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.error)

    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(uuid=genre.uuid, name=genre.name)


@router.get('/', response_model=List[Genre])
async def genre_list(genre_service: AbstractGenreService = Depends(get_genre_service)) -> List[Genre]:
    try:
        genres = await genre_service.get_all()
    except NotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=e.error)

    return [Genre(uuid=genre.uuid, name=genre.name) for genre in genres]
