import django_filters
from django.db.models import Q
from .models import Book, Genre
from django.core.exceptions import ValidationError


class GenreFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Genre
        fields = ["name"]


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    genre = django_filters.CharFilter(method="filter_genre")
    categories = django_filters.CharFilter(method="filter_categories")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Book
        fields = ["title", "author", "genre", "categories"]

    def filter_search(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset.none()

        return queryset.filter(
            Q(title__icontains=value)
            | Q(author__icontains=value)
            | Q(genre__name__icontains=value)
        )

    def filter_genre(self, queryset, name, value):
        genres = [genre.strip() for genre in value.split(",")]
        queries = [Q(genre__name__icontains=genre) for genre in genres]
        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)

    def filter_categories(self, queryset, name, value):
        categories = [category.strip() for category in value.split(",")]
        queries = [Q(categories__icontains=category) for category in categories]
        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)
