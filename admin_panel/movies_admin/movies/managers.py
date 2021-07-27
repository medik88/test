from django.db import models

from .choices import FilmworkType


class MovieManager(models.Manager):
    def get_queryset(self):
        return super(MovieManager, self).get_queryset().filter(work_type=FilmworkType.MOVIE)


class TVSeriesManager(models.Manager):
    def get_queryset(self):
        return super(TVSeriesManager, self).get_queryset().filter(work_type=FilmworkType.TV_SERIES)
