import orjson

from typing import Dict, List

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class LocalBaseModel(BaseModel):

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Film(LocalBaseModel):
    id: str
    title: str
    work_type: str
    description: str
    imdb_rating: float
    creation_date: str
    actors: Dict[str, str]
    directors: Dict[str, str]
    writers: Dict[str, str]
    actors_names: List[str]
    directors_names: List[str]
    writers_names: List[str]
    genres: List[str]


class Genre(LocalBaseModel):
    name: str


class Person(LocalBaseModel):
    id: str
    name: str


class Actor(Person):
    profession: str = 'Actor'


class Writer(Person):
    profession: str = 'Writer'


class Director(Person):
    profession: str = 'Director'
