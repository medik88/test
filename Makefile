test:
	newman run postman_test/async_api_tests.postman_collection.json

pytest:
	pytest tests
