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

# Послать запрос без параметров, проверить что что-то вернулось
@pytest.mark.asyncio
async def test_get_film_list(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 13
# Послать валидный запрос, страница 2, размер 5. Проверить пагинацию
@pytest.mark.asyncio
async def test_get_film_list_with_pagination(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=2&page[size]=5')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 3
# Послать запрос с невалидным page[number], проверить что ошибка
@pytest.mark.asyncio
async def test_get_film_list_not_valid_page(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=-1&page[size]=5')

    assert response.status == 422
# Послать запрос с невалидным page[size], проверить что ошибка
async def test_get_film_list_not_valid_pagesize(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('/film/?page[number]=1&page[size]=-5')

    assert response.status == 422
# Послать запрос с filter[genre] UUID жанра с фильмами, проверить что нет ошибки
async def test_get_film_list_with_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 7
# Послать запрос с валидным filter[genre] с UUID жанром без фильмов, проверить что вернулся пустой список
async def test_get_film_list_with_filter(event_loop, es_client_with_data, make_get_request):
    response = await make_get_request('film/?page[number]=1&page[size]=10&filter[genre]=0de7d079-2ddc-4c4a-9fb8-7d89bc7b53f3')

    assert response.status == 200
    validate(instance=response.body, schema=film_list_schema)
    assert len(response.body) == 0
# Послать запрос с несуществующим filter[genre] UUID. Проверить (тут интересно что мы должны вернуть: пустой список или ошибку)
# Послать запрос с невалидным filter[genre] UUID, проверить что ошибка.
# Послать запрос с параметров сортировки imdb_rating, проверить результат
# Послать запрос с параметров сортировки -imdb_rating, проверить результат
# Послать запрос с параметров сортировки title, проверить результат
# Послать запрос с параметров сортировки -title, проверить результат
# Послать запрос с невалидным параметров сортировки, проверить что ошибка



# Послать запрос с UUID фильма с персонами и жанрами, проверить результат
# Послать запрос с UUID фильма без персон и жанров, проверить результат
@pytest.mark.asyncio
async def test_get_film_by_valid_uuid(event_loop, es_client_with_data, make_get_request):
    valid_film_uuid = '2444b1b3-def9-4800-ac79-fd150b8a0dbd'

    response = await make_get_request(f'/film/{valid_film_uuid}/')

    assert response.status == 200
    validate(instance=response.body, schema=film_schema)
    assert response.body['uuid'] == valid_film_uuid
    assert response.body['title'] == 'Загадочная история Бенджамина Баттона'
# Послать запрос с несуществующим UUID, проверить что 404
@pytest.mark.asyncio
async def test_get_film_by_random_uuid(event_loop, es_client_with_data, make_get_request):
    random_uuid = '5c9b1b69-69b3-43fe-aa18-3666dd9d104b'

    response = await make_get_request(f'/film/{random_uuid}/')
    assert response.status == 404
# Послать запрос с невалидным UUID, проверить что 422
@pytest.mark.asyncio
async def test_get_film_by_invalid_uuid(event_loop, es_client_with_data, make_get_request):
    invalid_uuid = 'some_invalid_uuid'

    response = await make_get_request(f'/film/{invalid_uuid}/')
    assert response.status == 422



# Послать запрос с пустым query, проверить что ошибка
# Послать запрос с query 2 символа, проверить что ошибка
# Послать запрос с невалидным page[number], проверить что ошибка
# Послать запрос с невалидным page[size], проверить что ошибка
# Послать валидный запрос, страница 1, размер 50, проверить что вернулся список элементов, проверить схему
# Послать валидны запрос без указания страницы и размера, проверить
# Послать валидный запрос, страница 2, размер 5. Проверить что пагинация сработала правильно
# Послать запрос со сложным query, проверить что вернулся пустой список (не уверен что такой запрос можно будет составить, чтобы ES ничего не вернул)
# Послать два валидных запроса подряд, замерить время каждого запроса. Проверить что кэш сработал

