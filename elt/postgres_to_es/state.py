import abc
import json
import time
from datetime import datetime, timedelta
from typing import Any

import psycopg2
import redis
from config import settings
from redis import Redis


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def save_data(self, data: dict) -> None:
        pass

    @abc.abstractmethod
    def retrieve_data(self) -> dict:
        pass


class RedisStorage(BaseStorage):
    def __init__(self, redis_adapter: Redis):
        self.redis_adapter = redis_adapter

    def save_data(self, data: dict) -> None:
        self.redis_adapter.set("etl_data", json.dumps(data))

    def retrieve_data(self) -> dict:
        raw_data = self.redis_adapter.get("etl_data")
        if raw_data is None:
            return {}
        return json.loads(raw_data)


class State:
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.data = None

    def retrieve_data(self) -> dict:
        self.data = self.storage.retrieve_data()
        if not self.data:
            self.data = {}
        return self.data

    def set_state(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.storage.save_data(self.data)

    def get_state(self, key: str, default=None) -> Any:
        return self.data.get(key, default)


state = State(storage=RedisStorage(redis.from_url(settings.REDIS_DSN)))


def get_modified(entity: str) -> datetime:
    _ = state.retrieve_data()
    ts = state.get_state(entity)
    if ts is not None:
        return datetime.fromtimestamp(ts)
    return retrieve_from_db(entity)


def set_modified(modified: datetime, entity: str) -> None:
    _ = state.retrieve_data()
    ts = time.mktime(modified.timetuple()) + modified.microsecond / 1000000.0
    if ts > state.get_state(entity, 0):
        state.set_state(entity, ts)


def retrieve_from_db(entity: str) -> datetime:
    conn = psycopg2.connect(settings.POSTGRES_DSN)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT modified FROM movies_%s ORDER BY modified LIMIT 1" % entity
            )
            row = cur.fetchone()
            modified = row[0] - timedelta(microseconds=1)
            set_modified(modified, entity)
            return modified
    finally:
        conn.close()
