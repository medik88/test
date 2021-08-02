import asyncio
import json
import pathlib
from dataclasses import dataclass

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from multidict import CIMultiDictProxy

from .settings import settings


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    res = policy.new_event_loop()
    asyncio.set_event_loop(res)
    res._close = res.close
    res.close = lambda: None

    yield res

    res._close()


@pytest.fixture(autouse=True)
async def clear_cache():
    redis = await aioredis.create_redis_pool((settings.REDIS_HOST, settings.REDIS_PORT), minsize=10, maxsize=20)
    await redis.flushall()
    yield
    redis.close()
    await redis.wait_closed()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.ELASTIC_HOST)
    yield client
    await client.close()


def get_testdata_dir():
    return pathlib.Path(__file__).parent / 'testdata'


@pytest.fixture(scope='session')
async def es_client_with_data(es_client):
    await es_client.indices.delete('*')

    async def load_from_resource(schema_file_name: str, data_file_name: str, index_name: str):
        with open(get_testdata_dir() / schema_file_name, encoding='utf-8') as schema:
            await es_client.indices.create(index_name, schema.read())

        with open(get_testdata_dir() / data_file_name, encoding='utf-8') as file:
            items = json.load(file)
            await async_bulk(es_client, items['data'])

    await load_from_resource('es_schema_genres.json', 'es_data_genres.json', settings.ELASTIC_GENRES_INDEX)
    await load_from_resource('es_schema_movies.json', 'es_data_movies.json', settings.ELASTIC_MOVIES_INDEX)
    await load_from_resource('es_schema_persons.json', 'es_data_persons.json', settings.ELASTIC_PERSONS_INDEX)

    yield es_client


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture(scope='function')
def make_get_request(session):
    async def inner(method: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = settings.SERVICE_URL + '/api/v1' + method
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
