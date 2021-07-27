import datetime

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel, TimeStampedModel

from .choices import FilmworkType, Profession, ContentRating
from . import managers


class Genre(TimeStampedModel, UUIDModel):
    name = models.CharField(_('name'), max_length=20)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    def __str__(self):
        return self.name


class Filmwork(TimeStampedModel, UUIDModel):
    title = models.CharField(_('title'), max_length=255, db_index=True)
    description = models.TextField(_('description'), blank=True, default='')
    genres = models.ManyToManyField(Genre, verbose_name=_('genres'))
    work_type = models.CharField(_('type'), max_length=20, choices=FilmworkType.choices)
    file_path = models.FileField(_('file'), upload_to='film_works/', blank=True, null=True)
    content_rating = models.CharField(
        _('content rating'), max_length=20, choices=ContentRating.choices, blank=True, default='')
    release_date = models.DateField(_('release date'), blank=True, null=True)
    imdb_rating = models.DecimalField(_('IMDB rating'), validators=[MinValueValidator(0), MaxValueValidator(10)],
                                      max_digits=3, decimal_places=1, blank=True, null=True)

    class Meta:
        verbose_name = _('filmwork')
        verbose_name_plural = _('filmwork')
        ordering = ['title']

    def __str__(self):
        return self.title


class Movie(Filmwork):
    objects = managers.MovieManager()

    class Meta:
        proxy = True
        verbose_name = _('movie')
        verbose_name_plural = _('movies')

    def save(self, *args, **kwargs):
        self.work_type = FilmworkType.MOVIE
        super().save(*args, **kwargs)


class TVSeries(Filmwork):
    objects = managers.TVSeriesManager()

    class Meta:
        proxy = True
        verbose_name = _('TV series')
        verbose_name_plural = _('TV series')

    def save(self, *args, **kwargs):
        self.work_type = FilmworkType.TV_SERIES
        super().save(*args, **kwargs)

    @property
    def release_dates(self):
        return self.episodes.values_list('release_date', flat=True)


class Episode(models.Model):
    season = models.PositiveSmallIntegerField(_('season'), blank=True, null=True, default=1)
    number = models.PositiveSmallIntegerField(_('number'),)
    tv_series = models.ForeignKey(Filmwork, verbose_name=_('TV series'), related_name='episodes',
                                  on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=255, blank=True, default='', db_index=True)
    release_date = models.DateField(_('release date'), blank=True, null=True)

    class Meta:
        verbose_name = _('episode')
        verbose_name_plural = _('episode')
        unique_together = ['tv_series', 'season', 'number']
        ordering = ('tv_series', 'season', 'number',)

    def __str__(self):
        return _("Episode '{title}' of '{tv_series}' TV series").format(title=self.title, tv_series=self.tv_series)


class Person(TimeStampedModel, UUIDModel):
    first_name = models.CharField(_('first name'), max_length=30, default='', db_index=True)
    last_name = models.CharField(_('last_name'), max_length=30, default='', db_index=True)
    filmworks = models.ManyToManyField(Filmwork, through='PersonFilmwork', related_name='persons')

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        ordering = ('last_name', 'first_name',)

    def __str__(self):
        return ' '.join([self.first_name, self.last_name])


class PersonFilmwork(models.Model):
    filmwork = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    profession = models.CharField(_('profession'), max_length=20, choices=Profession.choices)

    class Meta:
        unique_together = ['filmwork', 'person', 'profession']

    def __repr__(self):
        profession = Profession(self.profession).label.capitalize()
        work_type = FilmworkType(self.filmwork.work_type).label
        return _("<{profession}: {person} in {work_type} '{filmwork}'>").format(
            profession=profession, person=self.person, work_type=work_type, filmwork=self.filmwork)

    def __str__(self):
        return self.__repr__()
