test:
	newman run postman_test/async_api_tests.postman_collection.json

pytest:
	cd tests/functional && pytest -p no:warnings .
