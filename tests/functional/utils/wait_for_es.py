import logging
import os
import sys
from logging import config as logging_config
from time import sleep

from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions
from urllib3.exceptions import NewConnectionError

# Todo: remove this temporary hack
tests_root = os.path.abspath(os.path.pardir)
sys.path.append(tests_root)

from functional.logconf import LOGGING
from functional.settings import settings

logging_config.dictConfig(LOGGING)
logger = logging.getLogger('tests')

MAX_ATTEMPTS = 30

exc = (ConnectionRefusedError, NewConnectionError, es_exceptions.ConnectionError)


def wait_for_es():
    counter = 0
    while counter < MAX_ATTEMPTS:
        try:
            counter += 1
            client = Elasticsearch(hosts=settings.ELASTIC_HOST)
            connected = client.ping()
            if connected:
                logger.info('SUCCESS! Connected to Elasticsearch in %s attempts.' % counter)
                return
        except exc as e:
            logger.info('[ATTEMPT %s] Wating for Elasticsearch to become available...' % counter)
            sleep(1)
            continue

    logger.error('Failed to establish connection to Elasticsearch.')


if __name__ == '__main__':
    wait_for_es()
