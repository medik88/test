import pytest
from jsonschema import validate

genre_schema = {
    'type': 'object',
    'properties': {
        'uuid': {'type': 'string'},
        'name': {'type': 'string'}
    },
    'required': ['uuid', 'name']
}

genre_list_schema = {
    'type': 'array',
    'items': genre_schema
}


@pytest.mark.asyncio
async def test_get_genre_by_valid_uuid(event_loop, es_client_with_data, make_get_request):
    valid_genre_uuid = '0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3'

    response = await make_get_request(f'/genre/{valid_genre_uuid}/')

    assert response.status == 200
    validate(instance=response.body, schema=genre_schema)
    assert response.body['uuid'] == valid_genre_uuid
    assert response.body['name'] == 'драма'


@pytest.mark.asyncio
async def test_get_genre_by_random_uuid(event_loop, es_client_with_data, make_get_request):
    random_uuid = '5c9b1b69-69b3-43fe-aa18-3666dd9d104b'

    response = await make_get_request(f'/genre/{random_uuid}/')
    assert response.status == 404


@pytest.mark.asyncio
async def test_get_genre_by_invalid_uuid(event_loop, es_client_with_data, make_get_request):
    invalid_uuid = 'some_invalid_uuid'

    response = await make_get_request(f'/genre/{invalid_uuid}/')
    assert response.status == 422


@pytest.mark.asyncio
async def test_get_genre_list(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/genre')

    assert response.status == 200
    validate(instance=response.body, schema=genre_list_schema)
    assert len(response.body) == 9
