# Запуск приложений с помощью Docker (Dev-окружение)

## 0. Выбор окружения

В проекте подгтовлены два типа рабочего окружения **dev** и **production**, которые передаются docker-compose как

```shell
docker-compose -f <ENVIRONMENT>.yml
```

где `<ENVIRONMENT>` -- **production.yml** для production и **dev.yml** для разработки. Например,

```shell
docker-compose -f production.yml check
```

## 1. Запуск контейнеров

Из директории с **dev.yml** запустите контейнеры:

```shell
docker-compose -f dev.yml up
```

Подготовьте статику и базу данных:

```shell
docker-compose -f dev.yml run --rm django python manage.py collectstatic
docker-compose -f dev.yml run --rm django python manage.py migrate
```

## 2. Импорт

Для импорта из SQLite в Postgresql выполните:

```shell
docker-compose -f dev.yml run --rm etl python load_data.py
```

## 3. Заполнение базы тестовыми данными

```shell
docker-compose -f dev.yml run --rm django python manage.py generate_catalog --entity=persons --quantity=1000
```
где в качестве `--entities` нужно сначала сделать `genres` и `persons`, т. к. они нужны для генерации фильмов, 
а затем `movies` и `tvseries`.