import logging
import os
import sys
from logging import config as logging_config
from time import sleep

import redis
from redis import exceptions as redis_exceptions

# Todo: remove this temporary hack
tests_root = os.path.abspath(os.path.pardir)
sys.path.append(tests_root)

from functional.logconf import LOGGING
from functional.settings import settings

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('tests')

MAX_ATTEMTS = 10
exc = (ConnectionRefusedError, ConnectionError, redis_exceptions.ConnectionError)


def wait_for_redis():
    counter = 0
    connected = False

    while counter < MAX_ATTEMTS or connected:
        try:
            counter += 1
            client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
            connected = client.ping()
        except exc as e:
            logger.info('[ATTEMPT %s] Wating for Redis to become available...' % counter)
            sleep(1)
            continue
        else:
            logger.info('SUCCESS! Connected to Redis in %s attempts.' % counter)
            return
    logger.error('Failed to establish connection to Redis.')


if __name__ == '__main__':
    wait_for_redis()
