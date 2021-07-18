from uuid import UUID
from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from film import BaseFilm

router = APIRouter()


class Person(BaseModel):
    uuid: UUID
    full_name: str
    role: str
    film_ids: List[UUID]


@router.get('/{uuid}', response_model=Person)  #TODO
async def person_details() -> Person:
    pass

@router.get('/{uuid}/film', response_model=List[BaseFilm])  #TODO
async def films_by_person() -> List[BaseFilm]:
    pass

@router.get('/search', response_model=List[Person])  #TODO
async def person_search_list() -> List[Person]:
    pass
