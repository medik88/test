import logging
import typing
from enum import Enum
from logging.config import fileConfig
from time import sleep

import backoff
import psycopg2
import sql_queries
import state
import utils
from config import settings
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions
from elasticsearch.helpers import bulk
from psycopg2.extras import DictCursor
from urllib3.exceptions import NewConnectionError, ProtocolError

fileConfig(settings.LOGGING_CONFIG_FILE)
logger = logging.getLogger("etl")

backoff_params = {
    "wait_gen": backoff.expo,
    "on_backoff": utils.backoff_hdlr,
    "factor": settings.BACKOFF_FACTOR,
    "max_value": settings.BACKOFF_MAX_WAIT,
}

pg_backoff_params = dict(backoff_params)
pg_backoff_params["exception"] = (
    psycopg2.InterfaceError,
    psycopg2.errors.AdminShutdown,
    psycopg2.OperationalError,
)

es_backoff_params = dict(backoff_params)
es_backoff_params["exception"] = (
    ConnectionRefusedError,
    NewConnectionError,
    ConnectionError,
    es_exceptions.ConnectionError,
    ConnectionResetError,
    ProtocolError,
)

pg_params = {
    "dsn": settings.POSTGRES_DSN,
    "cursor_factory": DictCursor,
}


class Entity(Enum):
    FILMWORK = "filmwork"
    PERSON = "person"
    GENRE = "genre"


class Producer:
    def __init__(self, target: typing.Coroutine) -> None:
        self.target = target
        self.counter = 0

    def produce(self) -> None:
        while True:
            self._produce(
                entity=Entity.FILMWORK.value, query=sql_queries.PRODUCE_FILMWORKS
            )
            self._produce(entity=Entity.PERSON.value, query=sql_queries.PRODUCE_PERSONS)
            self._produce(entity=Entity.GENRE.value, query=sql_queries.PRODUCE_GENRES)

            logger.info("Import cycle finished.\n%s" % (80 * "-"))
            sleep(settings.CHECK_DB_INTERVAL)

    @backoff.on_exception(**pg_backoff_params)
    def _produce(self, entity: str, query: str) -> None:
        conn = psycopg2.connect(**pg_params)

        self.counter = 0
        batch = []
        modified = state.get_modified(entity)

        try:
            with conn.cursor(name="etl") as cur:
                cur.itersize = settings.BATCH_SIZE
                cur.execute(query % modified)

                for row in cur:
                    batch.append(dict(row))
                    self.counter += 1
                    if len(batch) >= settings.BATCH_SIZE:
                        self.send_batch(self.target, batch, entity)

            # send remainders if batch is not full
            self.send_batch(self.target, batch, entity)
        finally:
            conn.close()

    def send_batch(
            self, target: typing.Coroutine, batch: list[dict], entity: str
    ) -> None:
        logger.info("Produced: %s rows for '%s' entity" % (self.counter, entity))
        target.send((batch, entity))
        batch.clear()
        sleep(settings.ITERATION_INTERVAL)


class Enricher:
    def __init__(self, target: typing.Coroutine, person_transofrmer: typing.Coroutine):
        self.target = target
        self.person_transformer = person_transofrmer

    @utils.coroutine
    def enrich(self):
        while True:
            batch, entity = yield
            if entity == Entity.FILMWORK.value:
                self.target.send((batch, entity))
            else:
                self._enrich(batch, entity)

    @backoff.on_exception(**pg_backoff_params)
    def _enrich(self, batch: list[dict[str, typing.Any]], entity: str):
        conn = psycopg2.connect(**pg_params)
        enriched_batch = []
        ids = ",".join(["'%s'" % p["id"] for p in batch])

        try:
            with conn.cursor(name="enrich") as cur:
                cur.itersize = settings.BATCH_SIZE
                query = getattr(sql_queries, "ENRICH_%sS" % entity.upper())
                cur.execute(query % ids)

                counter = 0
                for row in cur:
                    enriched_batch.append(dict(row))
                    if len(enriched_batch) >= settings.BATCH_SIZE:
                        self.target.send((enriched_batch, entity))
                        logger.info(
                            "Enriched %s records for %s entity"
                            % (len(enriched_batch), entity)
                        )
                        if entity == Entity.PERSON.value:
                            self.person_transformer.send(enriched_batch)
                        enriched_batch.clear()
                        sleep(settings.ITERATION_INTERVAL)
                    counter += 1

                if not counter:
                    logger.info("Nothing to enrich")

        finally:
            conn.close()


class Merger:
    def __init__(self, target: typing.Coroutine):
        self.target = target

    @utils.coroutine
    def merge(self):
        while True:
            logger.info("Merge")
            batch, entity = yield
            if len(batch) == 0:
                self.target.send(([], entity))
            else:
                self._merge(batch, entity)

    @backoff.on_exception(**pg_backoff_params)
    def _merge(self, batch: list[dict[str, typing.Any]], entity: str):
        conn = psycopg2.connect(**pg_params)
        merged_batch = []
        filmwork_ids = ",".join(["'%s'" % f["id"] for f in batch])

        try:
            with conn.cursor(name="merge") as cur:
                cur.itersize = settings.BATCH_SIZE
                cur.execute(sql_queries.MERGE % filmwork_ids)

                for row in cur:
                    merged_batch.append(dict(row))

            # send only when all data for given filmworks is fetched
            self.target.send((merged_batch, entity))
            merged_batch.clear()
            sleep(settings.ITERATION_INTERVAL)

        finally:
            conn.close()


@utils.coroutine
def transform_persons(target: typing.Coroutine) -> typing.Generator:
    while True:
        batch = yield
        persons_batch = {}

        for item in batch:
            if item['person_id'] not in persons_batch:
                person = {
                    'name': item['name'],
                    'modified': item['person_modified'],
                    'filmworks': [{'uid': item['id'], 'title': item['title'], 'imdb_rating': item['imdb_rating']}]
                }
            else:
                person = persons_batch[item['person_id']]
                person['name'] = item['name']
                person['modified'] = item['person_modified']
                person['filmworks'] += [{
                    'uid': item['id'],
                    'title': item['title'],
                    'imdb_rating': item['imdb_rating']
                }]
            persons_batch[item['person_id']] = dict(person)
        target.send(persons_batch)


@utils.coroutine
def transform(target: typing.Coroutine) -> typing.Generator:
    while True:
        logger.info("Transform")
        batch, entity = yield
        logger.info(
            "Transformer received %d rows for '%s' entity" % (len(batch), entity)
        )
        transformed_batch = {"filmworks": {}, "persons": {}, "genres": {}}

        for item in batch:
            film = transformed_batch["filmworks"].get(
                item["filmwork_id"],
                {
                    "actors": [],
                    "directors": [],
                    "writers": [],
                    "actors_names": [],
                    "directors_names": [],
                    "writers_names": [],
                    "genres": [],
                    "genres_ids": [],
                },
            )

            film["title"] = item["title"]
            film["description"] = item["description"]
            film["work_type"] = item["work_type"]
            film["imdb_rating"] = float(item["imdb_rating"])
            film["created"] = item["created"]
            film["modified"] = item["modified"]

            transformed_batch["filmworks"][item["filmwork_id"]] = film

            if "person_id" in item:
                person_name = item["person_name"]
                person = {"uid": item["person_id"], "name": person_name}
                if item["profession"] == "actor" and person not in film["actors"]:
                    film["actors"] += [person]
                    film["actors_names"] += [person_name]
                if item["profession"] == "director" and person not in film["directors"]:
                    film["directors"] += [person]
                    film["directors_names"] += [person_name]
                if item["profession"] == "writer" and person not in film["writers"]:
                    film["writers"] += [person]
                    film["writers_names"] += [person_name]

                transformed_batch["persons"][item["person_id"]] = dict(person)
                transformed_batch["persons"][item["person_id"]]["modified"] = item[
                    "person_modified"
                ]

            if "genre_name" in item:
                genre = {"uid": item["genre_id"], "name": item["genre_name"]}
                if genre not in film["genres"]:
                    film["genres"] += [genre]
                    film["genres_ids"] += [item["genre_id"]]

                transformed_batch["genres"][item["genre_id"]] = dict(genre)
                transformed_batch["genres"][item["genre_id"]]["modified"] = item[
                    "genre_modified"
                ]

        target.send((transformed_batch, entity))
        sleep(settings.ITERATION_INTERVAL)


class ESLoader:
    counter: int

    @utils.coroutine
    def load(self) -> None:
        while True:
            logger.info("Load")
            batch, entity = yield
            self._load(batch, entity)

    @backoff.on_exception(**es_backoff_params)
    def _load(self, batch, entity) -> None:
        self.client = Elasticsearch(hosts=settings.ES_HOST)
        self.client.cluster.health(wait_for_status="yellow")

        logger.info("Loader got %d filmworks" % len(batch["filmworks"]))
        self.counter = 0
        filmwork_batch = []

        for uid, pgfilm in batch["filmworks"].items():
            esfilm = {
                "_type": "_doc",
                "_index": settings.ES_FILMWORKS_INDEX,
                "_id": uid,
                "_source": pgfilm,
            }

            filmwork_batch.append(esfilm)
            self.counter += 1

        bulk(self.client, filmwork_batch)
        logger.info("Total: %d" % self.counter)

        person_batch = batch["persons"]
        if len(person_batch):
            person_docs = self.make_docs(person_batch, settings.ES_PERSONS_INDEX)
            bulk(self.client, person_docs)

        genre_batch = batch["genres"]
        if len(genre_batch):
            genre_docs = self.make_docs(genre_batch, settings.ES_GENRES_INDEX)
            bulk(self.client, genre_docs)
            state.set_modified(
                genre_docs[-1]["_source"]["modified"], Entity.GENRE.value
            )

        # save state for extractor
        if len(filmwork_batch):
            dt = filmwork_batch[-1]["_source"]["modified"]
            state.set_modified(dt, entity)

    def make_docs(self, data: dict[str, typing.Any], indice: str):
        docs = []
        for _, item in data.items():
            docs.append(
                {
                    "_type": "_doc",
                    "_index": indice,
                    "_id": item["uid"],
                    "_source": {
                        "name": item["name"],
                        "modified": item.pop("modified"),
                    },
                }
            )
        return docs


class PersonLoader:

    @utils.coroutine
    def load(self):
        while True:
            batch = yield
            self._load(batch)

    @backoff.on_exception(**es_backoff_params)
    def _load(self, batch):
        es = Elasticsearch(hosts=settings.ES_HOST)
        es.cluster.health(wait_for_status="yellow")
        person_docs = []

        for uid, pgperson in batch.items():
            esperson = {
                "_type": "_doc",
                "_index": settings.ES_PERSONS_INDEX,
                "_id": uid,
                "_source": pgperson,
            }
            person_docs.append(esperson)

        bulk(es, person_docs)
        state.set_modified(
            person_docs[-1]["_source"]["modified"], Entity.PERSON.value
        )


def run_etl():
    filmwork_loader = ESLoader()
    person_loader = PersonLoader()
    transformer = transform(filmwork_loader.load())
    person_transformer = transform_persons(person_loader.load())
    merger = Merger(transformer)
    enricher = Enricher(merger.merge(), person_transformer)
    producer = Producer(enricher.enrich())
    producer.produce()


if __name__ == "__main__":
    run_etl()
