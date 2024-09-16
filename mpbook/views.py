from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Genre, Book, PreviousSearch, BookView
from .serializers import GenreSerializer, BookSerializer, PreviousSearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters import rest_framework as filters
import django_filters
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10  # Default
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
            }
        )


# GenreFilter to filter based on genre name
class GenreFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Genre
        fields = ["name"]


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GenreFilter

    @action(detail=False, methods=["get"], url_path="search")
    def search_genre(self, request):
        # Use the filterset_class to filter based on the keyword
        filtered_queryset = self.filter_queryset(self.get_queryset())

        if filtered_queryset.exists():
            serializer = GenreSerializer(filtered_queryset, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        return Response(
            {"error": "No matching genres found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(detail=False, methods=["post"], url_path="selection")
    def validate_selection(self, request):
        genre_ids = request.data.get("genre_ids", [])

        # Check if the number of selected genres is at least four
        if len(genre_ids) < 4:
            return Response(
                {"error": "You must select at least four genres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure that all selected genre IDs are valid
        valid_genre_ids = Genre.objects.filter(id__in=genre_ids).values_list(
            "id", flat=True
        )
        if set(genre_ids) != set(valid_genre_ids):
            return Response(
                {"error": "One or more selected genres are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Selection is valid."}, status=status.HTTP_200_OK)


# BookFilter to filter based on title, author, and genre
class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = django_filters.CharFilter(field_name="author", lookup_expr="icontains")
    genre = django_filters.CharFilter(method="filter_genre")  # Handle multiple genres
    categories = django_filters.CharFilter(
        method="filter_categories"
    )  # Handle multiple categories
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Book
        fields = ["title", "author", "genre", "categories"]

    # Simplified search filter method
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)
            | Q(author__icontains=value)
            | Q(genre__icontains=value)
        )

    # Filter method to handle multiple genres (case-insensitive, partial match)
    def filter_genre(self, queryset, name, value):
        genres = [genre.strip() for genre in value.split(",")]  # Clean up spaces
        queries = [Q(genre__icontains=genre) for genre in genres]
        query = queries.pop()  # << Start with the first query, so pop is used >>
        for item in queries:
            query |= item  # << Combine queries with OR as to handle multiple searches match >>
        return queryset.filter(query)

    # Filter method to handle multiple categories (case-insensitive, partial match)
    def filter_categories(self, queryset, name, value):
        categories = [
            category.strip() for category in value.split(",")
        ]  # Clean up spaces
        queries = [Q(categories__icontains=category) for category in categories]
        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    pagination_class = CustomPagination

    @action(detail=False, methods=["get"], url_path="search")
    def search_books(self, request):
        search_query = request.query_params.get("search", "").strip()
        genre_query = request.query_params.get("genres", "").strip()
        category_query = request.query_params.get("categories", "").strip()

        # Check if the search query is empty
        if not search_query and not genre_query and not category_query:
            return Response(
                {"error": "Please provide a search query or filters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Start with all books
        queryset = self.get_queryset()

        # Apply the custom search filter via BookFilter
        filterset = self.filterset_class(
            data={
                "search": search_query,
                "genre": genre_query,
                "categories": category_query,
            },
            queryset=queryset,
        )

        if filterset.is_valid():
            filtered_queryset = filterset.qs

            if filtered_queryset.exists():
                # Record search history
                PreviousSearch.objects.create(user=request.user, query=search_query)

                # Paginate the filtered queryset
                page = self.paginate_queryset(filtered_queryset)
                if page is not None:
                    serializer = BookSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                # If pagination is not needed, return all results
                serializer = BookSerializer(filtered_queryset, many=True)
                return Response({"results": serializer.data}, status=status.HTTP_200_OK)

            return Response(
                {"error": "No results found for the provided search query."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"error": "Invalid search query or filters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # for rating | as if needed dinamically --|-->
    @action(detail=True, methods=["post"], url_path="rate")
    def rate_book(self, request, pk=None):
        book = self.get_object()
        rating = request.data.get("rating")

        # Validate that rating is present
        if rating is None:
            return Response(
                {"error": "Rating is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(book, data={"rating": rating}, partial=True)

        if serializer.is_valid():
            serializer.save()  # Handles updating the book's rating directly
            return Response(
                {"status": "Book rating updated", "new_rating": book.rating},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="view")
    def record_view(self, request, pk=None):
        book = self.get_object()

        viewer = (
            request.user if request.user.is_authenticated else None
        )  # Handle anonymous user

        try:
            # Create a new view record
            BookView.objects.create(
                book=book,
                viewer=viewer,  # None for anonymous users
                view_date=timezone.now(),
            )

            # Increment the book's view count
            book.views += 1
            book.save()

            return Response({"status": "Book view recorded"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # for trending >> books
    @action(detail=False, methods=["get"], url_path="trending")
    def trending_books(self, request):
        # Access 'is_trending' property without parentheses
        trending_books = [book for book in Book.objects.all() if book.is_trending]
        serializer = BookSerializer(trending_books, many=True)
        return Response({"trending": serializer.data}, status=status.HTTP_200_OK)

    # for recent_searches:
    @action(detail=False, methods=["get"], url_path="recent-searches")
    def recent_searches(self, request):
        recent_searches = PreviousSearch.objects.filter(user=request.user).order_by(
            "-searched_at"
        )[:10]
        serializer = PreviousSearchSerializer(recent_searches, many=True)
        return Response({"recent_searches": serializer.data}, status=status.HTTP_200_OK)

    # for past_record suggestion
    @action(detail=False, methods=["get"], url_path="suggestions")
    def suggestions(self, request):
        recent_searches = PreviousSearch.objects.filter(user=request.user).order_by(
            "-searched_at"
        )[:5]
        suggestions = Book.objects.none()

        for search in recent_searches:
            suggestions |= Book.objects.filter(
                Q(title__icontains=search.query) | Q(genre__icontains=search.query)
            )

        serializer = BookSerializer(suggestions.distinct(), many=True)
        return Response({"suggestions": serializer.data}, status=status.HTTP_200_OK)

    # for clearing the search records
    @action(detail=False, methods=["delete"], url_path="clear-history")
    def clear_search_history(self, request):
        PreviousSearch.objects.filter(user=request.user).delete()
        return Response(
            {"detail": "Search history cleared."}, status=status.HTTP_204_NO_CONTENT
        )
