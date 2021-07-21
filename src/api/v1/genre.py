from http import HTTPStatus
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)
    name: str = ''


@router.get('/{uuid}', response_model=Genre)
async def genre_details(uuid: UUID, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(uuid)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(uuid=genre.uuid, name=genre.name)


@router.get('/', response_model=List[Genre])
async def genre_list(genre_service: GenreService = Depends(get_genre_service)) -> List[Genre]:
    genres = await genre_service.get_all()
    return [Genre(uuid=genre.uuid, name=genre.name) for genre in genres]
