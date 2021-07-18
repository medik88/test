import uuid
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Genre(BaseModel):
    uuid: uuid.UUID
    name: str


@router.get('/', response_model=List[Genre])
async def genre_list() -> List[Genre]:
    # todo add getting list of genres here
    genre1 = Genre(uuid=1, name='Action')
    genre2 = Genre(uuid=2, name='Fiction')
    return [genre1, genre2]


@router.get('/{genre_uuid}', response_model=Genre)
async def genre_details(genre_uuid: uuid.UUID) -> Genre:
    # todo add getting genre info here
    return Genre(uuid=genre_uuid, name='Action')
