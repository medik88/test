from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, FloatField, Q, Value
from django.db.models.functions import Cast, Concat
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.choices import Profession
from movies.models import Filmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    def get_queryset(self):
        return super().get_queryset().prefetch_related('genres', 'personfilmwork_set__person').values(
            'id', 'title', 'description').annotate(
            creation_date=F('created'), rating=Cast('imdb_rating', output_field=FloatField()), type=F('work_type'),
            genres=ArrayAgg('genres__name', distinct=True),
            actors=ArrayAgg(Concat(F('persons__first_name'), Value(' '), F('persons__last_name')), distinct=True,
                            filter=Q(personfilmwork__profession=Profession.ACTOR)),
            directors=ArrayAgg(Concat(F('persons__first_name'), Value(' '), F('persons__last_name')), distinct=True,
                               filter=Q(personfilmwork__profession=Profession.DIRECTOR)),
            writers=ArrayAgg(Concat(F('persons__first_name'), Value(' '), F('persons__last_name')), distinct=True,
                             filter=Q(personfilmwork__profession=Profession.WRITER)),
        ).order_by('title')


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        return self.object


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = settings.MOVIES_PER_PAGE

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        context = {
            'count': paginator.count,
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None,
            'results': list(queryset),
        }
        return context
