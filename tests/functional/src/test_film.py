import pytest
from jsonschema import validate


film_schema = {
	"type": "object",
	"required": [
		"actors",
		"directors",
		"writers",
		"genres",
		"title",
		"description",
		"imdb_rating"
	],
	"properties": {
		"actors": {
			"type": "array",
			"items":{
				"type": "object",
				"required": [
					"uid",
					"name"
				],
				"properties": {
					"uid": {
						"type": "string",
					},
					"name": {
						"type": "string",
					}
				}
			}

		},
		"directors": {
			"type": "array",
		},
		"writers": {
			"type": "array",
			"items":{
				"type": "object",
				"required": [
					"uid",
					"name"
				],
				"properties": {
					"uid": {
						"type": "string",
					},
					"name": {
						"type": "string",
					}
				}
			}

		},
		"genres": {
			"type": "array",
			"items":{
				"type": "object",
				"required": [
					"uid",
					"name"
				],
				"properties": {
					"uid": {
						"type": "string",
					},
					"name": {
						"type": "string",
					}
				}
			}

		},
		"title": {
			"type": "string",
		},
		"description": {
			"type": "string",
		},
		"imdb_rating": {
			"type": "number",
		}
	}
}

film_schema_small = {
    "type": "object",
    "properties": {
        "uuid": {"type": "string"},
        "title": {"type": "string"},
        "imdb_rating": {"type": "number"}
    },
    "required": ["uuid", "title", "imdb_rating"]
  }

film_list_schema = {
    "type": "array",
    "items": film_schema_small
}

@pytest.mark.asyncio
async def test_get_film_list(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 13

@pytest.mark.asyncio
async def test_get_film_list_with_pagination(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=2&page[size]=5')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 5

@pytest.mark.asyncio
async def test_get_film_list_not_valid_page(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=A&page[size]=5')

    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_list_not_valid_pagesize(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=1&page[size]=B')

    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_list_valid_genre_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 7

@pytest.mark.asyncio
async def test_get_film_list_genre_without_film_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=2311d522-c5ab-4b2d-9db0-5c3b88a61fb7')

    assert response.status == 404

@pytest.mark.asyncio
async def test_get_film_list_not_exists_genre_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=7ed7d079-2ddc-4c4a-9fb8-7d89bc7b54d5')

    assert response.status == 404

@pytest.mark.asyncio
async def test_get_film_list_invalid_genre_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=abcdefgh')

    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_list_sort_by_imdb_rating(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=5&sort=imdb_rating')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 5
    imdb_rating = [i['imdb_rating'] for i in response.body]
    assert imdb_rating == [7.8, 8, 8, 8, 8.2]

@pytest.mark.asyncio
async def test_get_film_list_sort_by_reverse_imdb_rating(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=5&sort=-imdb_rating')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 5
    imdb_rating = [i['imdb_rating'] for i in response.body]
    assert imdb_rating == [8, 8, 7.8, 7.8, 7.7]

@pytest.mark.asyncio
async def test_get_film_list_sort_by_title(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=5&sort=title')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 5
    title = [i['title'] for i in response.body]
    assert title == [
        'Загадочная история Бенджамина Баттона',
        'Интервью с вампиром',
        'Одиннадцать друзей Оушена',
        'Остров проклятых',
        'Последний самурай'
    ]

@pytest.mark.asyncio
async def test_get_film_list_sort_by_reverse_title(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=5&sort=-title')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 5
    title = [i['title'] for i in response.body]
    assert title == [
        'Одиннадцать друзей Оушена',
        'Интервью с вампиром',
        'Загадочная история Бенджамина Баттона',
        'Друзья',
        'Выживший'
    ]

@pytest.mark.asyncio
async def test_get_film_list_invalid_sort(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=5&sort=43*3J')

    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_by_valid_uuid_with_persons_genres(event_loop, es_client_with_data, make_get_request):
    valid_film_uuid = '5d8960b3-b3a7-4137-9eaf-fa6129c9d0ff'

    response = await make_get_request(f'/film/{valid_film_uuid}/')

    assert response.status == 200
    validate(instance=response.body, schema=film_schema)
    assert response.body['uuid'] == valid_film_uuid
    assert response.body['title'] == 'Друзья'
    assert response.body['genres'][0]['name'] == 'Комедия'
    assert response.body['genres'][1]['name'] == 'мелодрама'
    assert response.body['actors'][0]['name'] == 'Мэтт ЛеБлан'
    assert response.body['actors'][1]['name'] == 'Дженифер Энистон'
    assert response.body['writers'][0]['name'] == 'Терес Уинтер'
    assert response.body['directors'][0]['name'] == 'Марк Райдер'

@pytest.mark.asyncio
async def test_get_film_by_valid_uuid_with_empty_persons_genres(event_loop, es_client_with_data, make_get_request):
    valid_film_uuid = '8839653a-f85e-486c-8e9f-54fc81b0c4cf'

    response = await make_get_request(f'/film/{valid_film_uuid}/')

    assert response.status == 200
    validate(instance=response.body, schema=film_schema)
    assert response.body['uuid'] == valid_film_uuid
    assert response.body['title'] == 'Терминатор'
    assert response.body['genres'] == []
    assert response.body['actors'] == []
    assert response.body['writers'] == []
    assert response.body['directors'] == []

@pytest.mark.asyncio
async def test_get_film_by_random_uuid(event_loop, es_client_with_data, make_get_request):
    random_uuid = '5c9b1b69-69b3-43fe-aa18-3666dd9d104b'

    response = await make_get_request(f'/film/{random_uuid}/')
    assert response.status == 404

@pytest.mark.asyncio
async def test_get_film_by_invalid_uuid(event_loop, es_client_with_data, make_get_request):
    invalid_uuid = 'some_invalid_uuid'

    response = await make_get_request(f'/film/{invalid_uuid}/')
    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_with_empty_query(event_loop, es_client_with_data, make_get_request):
    query = ''

    response = await make_get_request(f'/film/search?query={query}&page[number]=1&page[size]=5')
    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_with_two_sumbols_query(event_loop, es_client_with_data, make_get_request):
    query = 'hb'

    response = await make_get_request(f'/film/search?query={query}&page[number]=1&page[size]=5')
    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 0

@pytest.mark.asyncio
async def test_get_film_invalid_page_number_query(event_loop, es_client_with_data, make_get_request):
    query = 'терминатор'

    response = await make_get_request(f'/film/search?query={query}&page[number]=A&page[size]=5')
    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_invalid_page_size_query(event_loop, es_client_with_data, make_get_request):
    query = 'терминатор'

    response = await make_get_request(f'/film/search?query={query}&page[number]=1&page[size]=B')
    assert response.status == 422

@pytest.mark.asyncio
async def test_get_film_valid_query(event_loop, es_client_with_data, make_get_request):
    query = 'терминатор'

    response = await make_get_request(f'/film/search?query={query}&page[number]=1&page[size]=50')
    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 1

@pytest.mark.asyncio
async def test_get_film_without_page_and_size_query(event_loop, es_client_with_data, make_get_request):
    query = 'терминатор'

    response = await make_get_request(f'/film/search?query={query}')
    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 1

@pytest.mark.asyncio
async def test_get_film_valid_with_pagination_query(event_loop, es_client_with_data, make_get_request):
    query = 'кошка, которая гуляет сама по себе'

    response = await make_get_request(f'/film/search?query={query}&page[number]=2&page[size]=5')
    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 1

@pytest.mark.asyncio
async def test_get_film_complex_query(event_loop, es_client_with_data, make_get_request):
    query = 'человек'

    response = await make_get_request(f'/film/search?query={query}&page[number]=1&page[size]=50')
    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 0
