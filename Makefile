test:
	newman run postman_test/async_api_tests.postman_collection.json

pytest:
	cd tests/ && pytest -p no:warnings functional/src
