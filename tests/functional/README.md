# 0. Настройка параметров  

Параметры для тестов собраны в файле **settings.py**.
Для их перегрузки можно создать файл **tests/functional/.env** с новыми параметрами. За основу можно взять файл **tests/functional/.env.example**
```dotenv
export ELASTIC_HOST="127.0.0.1"
export REDIS_HOST="127.0.0.1"
```
Также можно указать параметры окружения при запуске в shell:
```shell
ELASTIC_HOST=127.0.0.1 REDIS_HOST=127.0.0.1 python main.py
```

Подготавливаем

```shell
cd tests
pip install -e .
```

После этого можно импортировать модули вот так

```python
from functional.logconf import LOGGING
from functional.settings import settings
```

Запустить тесты

```shell
cd tests/functional
pytest src
```

# 1. Запуск тестов с помощью Docker

Из каталога **functional**, где находится файл **docker-compose.py**, сначала собрать образы при необходимости:

```shell
docker-compose build
```

затем запустить

```shell
docker-compose up
```

Также, возможно, в целях отладки можно запустить окружение в контейнерах, а сам тест выполнить на хост-машине:

```shell
docker-compose up elastic redis api
```

а затем в отдельном терминале выполнить команду

```shell
pytest
```

предварительно активировав виртуальное окружение тестов (**tests/functional/requirements.txt**).
