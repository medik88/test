import orjson

from uuid import UUID
from typing import Dict, List

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class LocalBaseModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(LocalBaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genres: List[Dict[UUID, str]]
    actors: List[Dict[UUID, str]]
    writers: List[Dict[UUID, str]]
    directors: List[Dict[UUID, str]]
    work_type: str
    creation_date: str
    actors_names: List[str]
    directors_names: List[str]
    writers_names: List[str]


class Genre(LocalBaseModel):
    uuid: uuid.UUID
    name: str


class Person(LocalBaseModel):
    uuid: UUID
    full_name: str
    role: str
    film_ids: List[UUID]
