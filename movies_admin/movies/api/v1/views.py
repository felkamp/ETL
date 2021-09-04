from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView

from movies.models import FilmWork, PersonFilmWork, Role


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ["get"]

    def get_queryset(self):
        persons = (
            PersonFilmWork.objects.values("film_work_id", "role")
            .annotate(persons=ArrayAgg("person__full_name"))
            .filter(film_work_id=OuterRef("pk"))
        )
        genres = (
            FilmWork.objects.values("id")
            .annotate(genres=ArrayAgg("genres__name"))
            .filter(id=OuterRef("pk"))
        )
        return (
            FilmWork.objects.all()
            .values("id", "title", "description", "creation_date", "rating", "type")
            .annotate(genres=Subquery(genres.values("genres")))
            .annotate(actors=Coalesce(Subquery(persons.filter(role=Role.ACTOR).values("persons")), Value([])))
            .annotate(directors=Coalesce(Subquery(persons.filter(role=Role.PRODUCER).values("persons")), Value([])))
            .annotate(writers=Coalesce(Subquery(persons.filter(role=Role.SCREENWRITER).values("persons")), Value([])))
            .order_by("id")
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )

        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(page.object_list),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, object):
        return object
