from typing import List, Optional
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class LocalBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Genre(LocalBaseModel):
    uuid: UUID
    name: str


class FilmForPerson(LocalBaseModel):
    uid: UUID
    title: str
    imdb_rating: float


class Person(LocalBaseModel):
    uuid: UUID
    name: str
    filmworks: Optional[List[FilmForPerson]]


class PersonShort(LocalBaseModel):
    uid: UUID
    name: str


class GenreShort(LocalBaseModel):
    uid: UUID
    name: str


class Film(LocalBaseModel):
    uuid: UUID
    title: str
    imdb_rating: float
    description: str
    genres: List[GenreShort]
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]
    work_type: str
    created: str
    actors_names: List[str]
    directors_names: List[str]
    writers_names: List[str]
