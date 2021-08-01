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

Запустить тесты

```shell
make pytest
```
