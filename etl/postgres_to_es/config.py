from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    POSTGRES_DSN: PostgresDsn
    REDIS_DSN: RedisDsn
    BATCH_SIZE: int = 2000
    ES_HOST: str = "127.0.0.1:9200"

    LOGGING_CONFIG_FILE = "logging.ini"
    MAX_BACKOFF_DECAY = 60
    ITERATION_INTERVAL = 0.5
    CHECK_DB_INTERVAL = 3
    BACKOFF_FACTOR = 0.1
    BACKOFF_MAX_WAIT = 10
    ES_FILMWORKS_INDEX = "movies"
    ES_PERSONS_INDEX = "persons"
    ES_GENRES_INDEX = "genres"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "etl_"
        fields = {
            "POSTGRES_DSN": {
                "env": "POSTGRES_DSN",
            },
            "REDIS_DSN": {
                "env": "REDIS_DSN",
            },
            "ES_HOST": {
                "env": "ES_HOST",
            },
            "BATCH_SIZE": {"env": "BATCH_SIZE"},
        }


settings = Settings()
