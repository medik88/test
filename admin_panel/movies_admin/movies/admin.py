from django.contrib import admin
from django.template.defaultfilters import truncatechars
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import models


@admin.display(description=_('описание'))
def short_description(obj):
    return truncatechars(obj.description, 40)


@admin.display(description=_('content rating'))
def content_rating(obj):
    return obj.content_rating.value


class PersonProfessionInline(admin.TabularInline):
    model = models.PersonFilmwork
    extra = 0
    autocomplete_fields = ('person',)


class EpisodeInline(admin.TabularInline):
    model = models.Episode
    extra = 0


@admin.register(models.Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'content_rating', short_description,)
    autocomplete_fields = ('genres',)
    search_fields = ('title',)
    ordering = ('title',)
    fields = ('title', 'description', 'genres', 'file_path', 'content_rating', 'release_date', 'imdb_rating',)

    inlines = [
        PersonProfessionInline,
    ]


@admin.register(models.TVSeries)
class TVSeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_rating', short_description,)
    autocomplete_fields = ('genres',)
    search_fields = ('title',)
    ordering = ('title',)
    fields = ('title', 'description', 'genres', 'file_path', 'content_rating', 'imdb_rating',)

    inlines = [
        EpisodeInline,
        PersonProfessionInline,
    ]


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', short_description)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',)
    search_fields = ('last_name', 'first_name',)

    readonly_fields = ('filmography',)

    @admin.display(description=_('filmography'))
    def filmography(self, instance):
        return format_html_join(
            mark_safe('<br>'),
            _("'{}', {}, {}"),
            ((pf.filmwork.title, pf.filmwork.get_work_type_display(), pf.profession.capitalize())
             for pf in instance.personfilmwork_set.all().order_by('filmwork')),
        ) or mark_safe('<span class="errors">Could not find any filmwork.')
        # return instance.peronfilmwork_set.first()
