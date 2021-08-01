import time

import pytest
from jsonschema import validate

genre_schema = {
    "type": "object",
    "properties": {
        "uuid": {"type": "string"},
        "name": {"type": "string"}
    },
    "required": ["uuid", "name"]
}

genre_list_schema = {
    "type": "array",
    "items": genre_schema
};


@pytest.mark.asyncio
async def test_get_genre_by_valid_uuid(event_loop, es_client_with_data, make_get_request, clear_cache):
    valid_genre_uuid = '0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3'

    response = await make_get_request(f'/genre/{valid_genre_uuid}/')

    assert response.status == 200
    validate(instance=response.body, schema=genre_schema)
    assert response.body['uuid'] == valid_genre_uuid
    assert response.body['name'] == 'драма'


@pytest.mark.asyncio
async def test_get_genre_by_random_uuid(event_loop, es_client_with_data, make_get_request, clear_cache):
    random_uuid = '5c9b1b69-69b3-43fe-aa18-3666dd9d104b'

    response = await make_get_request(f'/genre/{random_uuid}/')
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_genre_by_invalid_uuid(event_loop, es_client_with_data, make_get_request, clear_cache):
    invalid_uuid = 'some_invalid_uuid'

    response = await make_get_request(f'/genre/{invalid_uuid}/')
    assert response.status == 422


@pytest.mark.asyncio
async def test_get_genre_by_uuid_cache(event_loop, es_client_with_data, make_get_request, clear_cache):
    valid_genre_uuid = '0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3'

    time1_start = time.time()
    response1 = await make_get_request(f'/genre/{valid_genre_uuid}/')
    time1_end = time.time()
    response2 = await make_get_request(f'/genre/{valid_genre_uuid}/')
    time2_end = time.time()

    time1 = time1_end - time1_start
    time2 = time2_end - time1_end

    assert time2 * 1.5 < time1
    assert response1.status == 200
    assert response1 == response2


@pytest.mark.asyncio
async def test_get_genre_list(event_loop, es_client_with_data, make_get_request, clear_cache):
    response = await make_get_request('/genre')

    assert response.status == 200
    validate(instance=response.body, schema=genre_list_schema)
    # assert len(response.body) == 8
