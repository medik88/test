import logging

from django.core.management import BaseCommand

from movies import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info(f'deleted genres {models.Genre.objects.all().delete()}')
        models.Movie.objects.all()
        logger.info(f'deleted movies {models.Movie.objects.all().delete()}')
        models.TVSeries.objects.all()
        logger.info(f'deleted TV series {models.TVSeries.objects.all().delete()}')
        models.Person.objects.all()
        logger.info(f'deleted persons {models.Person.objects.all().delete()}')
