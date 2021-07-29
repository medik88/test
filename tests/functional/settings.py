import pathlib

from pydantic import BaseSettings


class Settings(BaseSettings):
    ELASTIC_HOST: str = 'elasticsearch:9200'
    REDIS_HOST: str = 'redis'
    REDIS_PORT: str = '6379'
    SERVICE_URL: str = 'http://api:8000'

    class Config:
        # search .env file in current dir
        env_file = pathlib.Path(__file__).parent.resolve() / '.env'
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
            'SERVICE_URL': {
                'env': 'SERVICE_URL'
            }
        }


settings = Settings()
