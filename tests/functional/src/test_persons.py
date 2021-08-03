import logging
import uuid
from logging import config as logging_config

import pytest
from jsonschema import validate

from functional.logconf import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


short_film_schema = {
    'type': 'object',
    'required': ['uuid', 'title', 'imdb_rating'],
    'properties': {
        'uuid': {'type': 'string'},
        'title': {'type': 'string'},
        'imdb_rating': {'type': 'number'},
    },
}

person_schema = {
    'type': 'object',
    'properties': {
        'uuid': {'type': 'string'},
        'full_name': {'type': 'string'},
        'films': {'type': 'array', 'items': short_film_schema},
    },
    'required': ['uuid', 'full_name', 'films'],
}

person_list_schema = {'type': 'array', 'items': person_schema}


@pytest.mark.asyncio
async def test_get_person_by_valid_id(
    event_loop, es_client_with_data, make_get_request
):
    valid_person_uuid = 'c3fbdcf1-ead1-4dd6-8169-4f5151005487'

    response = await make_get_request(f'/person/{valid_person_uuid}')

    assert response.status == 200
    validate(instance=response.body, schema=person_schema)
    assert response.body['uuid'] == valid_person_uuid
    assert response.body['full_name'] == 'Брэд Питт'


@pytest.mark.asyncio
async def test_get_person_by_random_uuid(
    event_loop, es_client_with_data, make_get_request
):
    random_uuid = uuid.uuid4()

    response = await make_get_request(f'/person/{random_uuid}/')
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_person_by_invalid_uuid(
    event_loop, es_client_with_data, make_get_request
):
    invalid_uuid = 'some_invalid_uuid'

    response = await make_get_request(f'/person/{invalid_uuid}/')
    assert response.status == 422


@pytest.mark.asyncio
async def test_person_with_films(event_loop, es_client_with_data, make_get_request):
    uuid_of_person_with_films = 'c3fbdcf1-ead1-4dd6-8169-4f5151005487'

    response = await make_get_request(f'/person/{uuid_of_person_with_films}/film/')
    assert len(response.body) > 0


@pytest.mark.asyncio
async def test_person_without_films(event_loop, es_client_with_data, make_get_request):
    uuid_of_person_with_films = 'e633200c-666a-454a-a721-5b807d991fa6'

    response = await make_get_request(f'/person/{uuid_of_person_with_films}/film/')
    assert len(response.body) == 0


@pytest.mark.asyncio
async def test_person_films_with_random_uuid(
    event_loop, es_client_with_data, make_get_request
):
    random_uuid = uuid.uuid4()

    response = await make_get_request(f'/person/{random_uuid}/film/')
    assert response.status == 404


@pytest.mark.asyncio
async def test_person_films_with_invalid_uuid(
    event_loop, es_client_with_data, make_get_request
):
    invalid_uuid = 'invalid_uuid'

    response = await make_get_request(f'/person/{invalid_uuid}/film/')
    assert response.status == 422
