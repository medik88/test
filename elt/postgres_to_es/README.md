# Конфигурация

Задайте следующие переменные окружения:

- `POSTGRES_DSN`
- `REDIS_DSN`

либо создайте файл **compose/etl.env** с этими переменными, например:

```dotenv
export POSTGRES_DSN=postgres://user:pass@127.0.0.1:5432/dbname
export REDIS_DSN=redis://127.0.0.1:6379/1
```

или скопируйте образец

```shell
cp .envs/example.env .envs/etl.env
cp .envs/postgres.example.env .envs/postgres.env
```

После чего пересоберите образ **etl_service**:

```shell
docker-compose build
```

# Запуск службы

```shell
docker-compose up
```

# Создание индекса Elasticsearch

Если индекс еще не создан, его нужно создать. Но предварительно убедитесь, что Elastcisearch запущен с помощью команды:

```shell
docker-compose run --rm curl elasticsearch:9200
```
ответ должен быть примерно такой:

```shell
Creating etl_elasticsearch_run ... done
{
  "name" : "80ce14dbdefd",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "_4ENDC6DRTKwXaB1YYUA-A",
  "version" : {
    "number" : "7.13.3",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "5d21bea28db1e89ecc1f66311ebdec9dc3aa7d64",
    "build_date" : "2021-07-02T12:06:10.804015202Z",
    "build_snapshot" : false,
    "lucene_version" : "8.8.2",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

После этого запустите команду:

```shell
sed 's/127.0.0.1/elasticsearch/g' ./compose/elasticsearch/es_schema.txt | docker-compose run --rm elasticsearch bash
```
Сообщение о создании индекса:

```shell
Creating etl_elasticsearch_run ... done
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  2856  100    65  100  2791    228   9827 --:--:-- --:--:-- --:--:-- 10056
{"acknowledged":true,"shards_acknowledged":true,"index":"movies"}
```