import asyncio
import json
from dataclasses import dataclass
from importlib import resources

import aiohttp
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


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.ELASTIC_HOST)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def es_client_with_data(es_client):
    await es_client.indices.delete('*')

    async def load_from_resource(schema_file_name: str, data_file_name: str, index_name: str):
        with resources.open_text('testdata', schema_file_name) as schema:
            await es_client.indices.create(index_name, schema.read())

        with resources.open_text('testdata', data_file_name) as file:
            data = file.read()
            items = json.loads(data)
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


@pytest.fixture
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
