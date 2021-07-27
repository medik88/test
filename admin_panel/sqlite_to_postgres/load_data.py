import json
import logging
import os
import sqlite3
import typing
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, fields, asdict
from decimal import Decimal
from enum import Enum
from functools import cached_property
from logging.config import fileConfig

import psycopg2
from psycopg2._psycopg import cursor
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

psycopg2.extras.register_uuid()

logging_config = os.environ.get('LOG_CONFIG')
if logging_config:
    fileConfig(logging_config)
logger = logging.getLogger(__name__)

NA = 'N/A'


class Profession(Enum):
    ACTOR = 'actor'
    DIRECTOR = 'director'
    WRITER = 'writer'


@dataclass
class Genre:
    __slots__ = ['uid', 'name']
    uid: uuid.UUID
    name: str


@dataclass
class GenreMovie:
    __slots__ = ['uid', 'genre', 'filmwork']
    genre: uuid.UUID
    filmwork: uuid.UUID


@dataclass
class Person:
    __slots__ = ['uid', 'first_name', 'last_name']
    uid: uuid.UUID
    first_name: str
    last_name: str


@dataclass
class PersonMovie:
    __slots__ = ['uid', 'person', 'filmwork', 'profession']
    person: uuid.UUID
    filmwork: uuid.UUID
    profession: str


@dataclass
class Movie:
    __slots__ = ['uid', 'original_id', 'title', 'description', 'imdb_rating']
    uid: uuid.UUID
    original_id: str
    title: str
    description: typing.Optional[str]
    imdb_rating: typing.Optional[Decimal]

    @staticmethod
    def dict_factory(data):
        return dict((k, v) for k, v in data if not k == 'original_id')


class SQLiteLoader:
    conn: sqlite3.Connection
    cur: sqlite3.Cursor
    data: typing.DefaultDict

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.conn.row_factory = sqlite3.Row
        self.data = defaultdict(list)

    def load_movies(self) -> typing.DefaultDict:

        self.cur = self.conn.cursor()
        self.cur.execute('SELECT id, title, plot, imdb_rating, genre, writer, writers, director FROM movies')

        persons = defaultdict(set)
        genres = defaultdict(set)

        for row in self.cur.fetchall():
            self.data['filmwork'].append(self.get_filmwork(row))

            self.collect_genres(genres, row)
            self.collect_writers(persons, row)
            self.collect_directors(persons, row)

        self.collect_actors(persons)

        self.load_genres(genres)
        self.load_persons(persons)

        self.cur.close()

        logger.info(f"{len(self.data['filmwork'])} filmworks")
        logger.info(f"{len(self.data['genre'])} genres")
        logger.info(f"{len(self.data['filmwork_genres'])} filmwork_genres relations")
        logger.info(f"{len(self.data['person'])} persons")
        logger.info(f"{len(self.data['personfilmwork'])} personfilmwork relations")

        return self.data

    def get_filmwork(self, row) -> Movie:
        return Movie(
            uid=uuid.uuid4(),
            original_id=row['id'],
            title=row['title'],
            description='' if not row['plot'] or row['plot'] == NA else row['plot'],
            imdb_rating=None if not row['imdb_rating'] or row['imdb_rating'] == NA else Decimal(row['imdb_rating'])
        )

    @cached_property
    def get_writers_map(self) -> dict:
        self.cur.execute('SELECT id, name FROM writers')
        return dict(self.cur.fetchall())

    @cached_property
    def get_filmworks_map(self) -> dict:
        filmworks_map = defaultdict()
        for filmwork in self.data['filmwork']:
            filmworks_map[filmwork.original_id] = filmwork.uid
        return filmworks_map

    def collect_genres(self, genres: typing.DefaultDict, row: sqlite3.Row) -> None:
        for name in row['genre'].split(', '):
            genres[name].add(row['id'])

    def collect_writers(self, writers: typing.DefaultDict, row: sqlite3.Row) -> None:
        writer_original_ids = [row['writer']] if row['writer'] else [dct['id'] for dct in json.loads(row['writers'])]
        for original_id in writer_original_ids:
            writers[self.get_writers_map[original_id]].add((row['id'], Profession.WRITER.value))

    def collect_directors(self, directors: typing.DefaultDict, row: sqlite3.Row) -> None:
        if not row['director'] or row['director'] == NA:
            return
        for name in row['director'].split(', '):
            directors[name].add((row['id'], Profession.DIRECTOR.value))

    def collect_actors(self, actors: typing.DefaultDict) -> None:
        self.cur.execute('''SELECT ma.movie_id, ma.actor_id, a.name FROM actors a
            JOIN movie_actors ma ON a.id = actor_id''')
        for row in self.cur.fetchall():
            actors[row['name']].add((row['movie_id'], Profession.ACTOR.value))

    def load_genres(self, genres: dict) -> None:
        for name, filmworks in genres.items():
            genre = Genre(
                uid=uuid.uuid4(),
                name=name
            )
            for original_id in filmworks:
                self.data['filmwork_genres'].append(GenreMovie(
                    genre=genre.uid,
                    filmwork=self.get_filmworks_map[original_id]
                ))
            self.data['genre'].append(genre)

    def load_persons(self, persons: dict) -> None:
        for full_name, filmwork_professions in persons.items():
            if full_name == NA:
                continue

            first_name, last_name = self.split_full_name(full_name)
            person = Person(
                uid=uuid.uuid4(),
                first_name=first_name,
                last_name=last_name
            )
            for original_id, profession in filmwork_professions:
                self.data['personfilmwork'].append(PersonMovie(
                    person=person.uid,
                    filmwork=self.get_filmworks_map[original_id],
                    profession=profession
                ))
            self.data['person'].append(person)

    def split_full_name(self, full_name):
        if full_name is None:
            return '', ''
        splitted = full_name.rsplit(' ', 1)
        if len(splitted) == 1:
            return splitted[0], ''
        return splitted


class PostgresSaver:
    conn: _connection
    cur: cursor = None
    data: dict = field(default_factory=dict)
    filmworks_id_map: dict = field(default_factory=dict)

    def __init__(self, conn: _connection):
        self.conn = conn

    def save_all_data(self, data: typing.DefaultDict):
        self.cur = self.conn.cursor()
        self.data = data

        self.save_table(Movie, 'filmwork', ['id', 'title', 'description', 'imdb_rating',])
        self.save_table(Genre, 'genre')
        self.save_table(GenreMovie, 'filmwork_genres', ['genre_id', 'filmwork_id'])
        self.save_table(Person, 'person')
        self.save_table(PersonMovie, 'personfilmwork', ['person_id', 'filmwork_id', 'profession'])

    def save_table(self, klass: dataclass, table_name: str, table_fields: list[str] = None):
        arguments = []
        for obj in self.data[table_name]:
            factory = getattr(obj, 'dict_factory', dict)
            arguments.append(asdict(obj, dict_factory=factory))
        template = ','.join([f'%({f.name})s' for f in fields(klass) if not f.name == 'original_id'])
        values = ','.join(self.cur.mogrify(f'({template})', a).decode('utf-8') for a in arguments)
        field_str = '(%s)' % ', '.join(table_fields) if table_fields else ''
        query = f'INSERT INTO movies_{table_name} {field_str} VALUES {values}'
        self.cur.execute(query)
        logger.info(f'{table_name}s saved: {self.cur.rowcount}')


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('POSTGRES_NAME', default='movies'),
        'user': os.environ.get('POSTGRES_USER', default='postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('POSTGRES_HOST', default='127.0.0.1'),
        'port': os.environ.get('POSTGRES_PORT', default=5432),
        'options': os.environ.get('POSTGRES_OPTIONS'),
    }
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
