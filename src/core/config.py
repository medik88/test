import os
from logging import config as logging_config

from core.logger import LOGGING

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_CACHE_EXPIRE_S = int(os.getenv('REDIS_CACHE_EXPIRE_S', 60 * 5))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'elastic')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))
ELASTIC_MOVIES_INDEX = os.getenv('ELASTIC_MOVIES_INDEX', 'movies')
ELASTIC_PERSONS_INDEX = os.getenv('ELASTIC_PERSONS_INDEX', 'persons')
ELASTIC_GENRES_INDEX = os.getenv('ELASTIC_GENRES_INDEX', 'genres')

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE_SIZE = 20
