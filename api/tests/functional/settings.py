from pydantic import BaseSettings


class Settings(BaseSettings):
    ELASTIC_HOST: str = 'elasticsearch:9200'
    REDIS_HOST: str = 'redis'
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
            }
        }


settings = Settings()
