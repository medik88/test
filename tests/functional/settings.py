from pydantic import BaseSettings


class Settings(BaseSettings):
    ELASTIC_HOST: str = 'elastic:9200'
    REDIS_HOST: str = 'redis'
    REDIS_DB: str = 0
    REDIS_PORT: str = '6379'

    class Config:
        env_file = '.env'
        env_file_encoding = "utf-8"
        fields = {
            'ELASTIC_HOST': {
                'env': 'ELASTIC_HOST'
            },
            'REDIS_HOST': {
                'env': 'REDIS_HOST'
            },
            'REDIS_PORT': {
                'env': 'REDIS_PORT'
            },
            'REDIS_DB': {
                'env': 'REDIS_DB'
            },
        }


settings = Settings()
