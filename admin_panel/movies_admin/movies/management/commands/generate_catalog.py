import logging
import random
from datetime import timedelta
from math import ceil

from django.core.management import BaseCommand
from faker import Faker
from mixer.backend.django import mixer
from timeit import default_timer as timer

from movies.choices import Profession
from movies.models import PersonFilmwork, Genre, Person, TVSeries

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


def simple_timer(func):
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        elapsed = timedelta(seconds=timer() - start)
        logger.info(f'time elapsed: {elapsed}')
        return result

    return wrapper


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--entity',
            choices=['genres', 'persons', 'movies', 'tvseries', 'users'],
            required=True
        )
        parser.add_argument(
            '--quantity',
            type=int,
            help='Should be divisible by 1000',
            required=True
        )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()
        Faker.seed(0)
        self.content_ratings = mixer.sequence('0+', '2+', '6+', '12+', '14', '16+', '18+')

    def handle(self, *args, **options):
        entity = options['entity']
        quantity = options['quantity']

        getattr(self, f'generate_{entity}')(quantity)

    @property
    def random_rating(self):
        return round(random.uniform(1, 9.9), 1)

    @simple_timer
    def generate_movies(self, quantity):
        cycles = ceil(quantity / BATCH_SIZE)

        genres = list(Genre.objects.all())
        if not len(genres):
            logger.error('No genres found')
            return
        persons = list(Person.objects.all())
        if not len(persons):
            logger.error('No persons found')
            return

        for i in range(cycles):
            relations = []
            for _ in range(BATCH_SIZE):
                movie = mixer.blend(
                    'movies.movie',
                    description=mixer.FAKE,
                    content_rating=self.content_ratings,
                    release_date=mixer.FAKE,
                    imdb_rating=self.random_rating,
                )
                relations += self.generate_filmwork_relations(movie, genres, persons)
            logger.info(f'generated {(i + 1) * BATCH_SIZE} movies')
            PersonFilmwork.objects.bulk_create(relations)

    @simple_timer
    def generate_tvseries(self, quantity):
        self.set_up()
        cycles = ceil(quantity / BATCH_SIZE)

        genres = list(Genre.objects.all())
        if not len(genres):
            logger.error('No genres found')
            return
        persons = list(Person.objects.all())
        if not len(persons):
            logger.error('No persons found')
            return

        for i in range(cycles):
            relations = []
            for _ in range(BATCH_SIZE):
                rating = self.random_rating
                tvseries = mixer.blend(
                    'movies.tvseries',
                    description=mixer.FAKE,
                    content_rating=self.content_ratings,
                    imdb_rating=rating,
                )
                relations += self.generate_filmwork_relations(tvseries, genres, persons)
            logger.info(f'generated {(i + 1) * BATCH_SIZE} TV series')
            PersonFilmwork.objects.bulk_create(relations)

    def generate_filmwork_relations(self, filmwork, genres, persons):
        self.set_up()
        filmwork_genres = self.fake.random_elements(
            elements=genres, length=(round(random.uniform(1, 5))), unique=True)
        filmwork.genres.set(filmwork_genres)
        fake_persons = self.fake.random_elements(
            elements=persons, length=(round(random.uniform(1, 5))), unique=True)
        relations = []
        for p in fake_persons:
            relations.append(PersonFilmwork(
                filmwork_id=filmwork.id, person_id=p.id,
                profession=self.fake.random_element([k for k, v in Profession.choices])
            ))
        if isinstance(filmwork, TVSeries):
            for i in range(round(random.uniform(1, 10))):
                mixer.blend(
                    'movies.episode', tv_series=filmwork, title=mixer.FAKE, release_date=mixer.FAKE,
                    season=round(random.uniform(1, 5)), number=i + 1)
        return relations

    @simple_timer
    def generate_genres(self, quantity):
        genres = mixer.cycle(quantity).blend('movies.genre', name=self.fake.word)
        logger.info(f"generated {quantity} genres")
        return genres

    @simple_timer
    def generate_persons(self, quantity):
        persons = mixer.cycle(quantity).blend('movies.person', first_name=mixer.FAKE, last_name=mixer.FAKE)
        logger.info(f"generated {quantity} persons")
        return persons

    def generate_users(self, quantity):
        mixer.cycle(quantity).blend('auth.user')

    def set_up(self):
        if not Genre.objects.count():
            self.generate_genres(10)
        if not Person.objects.count():
            self.generate_persons(10)
