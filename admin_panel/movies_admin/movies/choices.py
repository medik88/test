from django.db import models
from django.utils.translation import gettext_lazy as _


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('movie')
    TV_SERIES = 'tv_series', _('TV series')


class Profession(models.TextChoices):
    ACTOR = 'actor', _('actor')
    DIRECTOR = 'director', _('director')
    WRITER = 'writer', _('writer')


class ContentRating(models.TextChoices):
    R0 = '0+', _('0+')
    R2 = '2+', _('2+')
    R6 = '6+', _('6+')
    R12 = '12+', _('12+')
    R14 = '14+', _('14+')
    R16 = '16+', _('16+')
    R18 = '18+', _('18+')
