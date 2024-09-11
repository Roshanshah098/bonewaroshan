from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Genre, Book, PreviousSearch
from .serializers import GenreSerializer, BookSerializer, PreviousSearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters import rest_framework as filters


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
class BookFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")
    author = filters.CharFilter(field_name="author", lookup_expr="icontains")
    genre = filters.CharFilter(field_name="genre", lookup_expr="icontains")
    search = filters.CharFilter(method='filter_search')

    class Meta:
        model = Book
        fields = ["title", "author", "genre"]

    def filter_search(self, queryset, name, value): 
        return queryset.filter(
            Q(title__icontains=value) |
            Q(author__icontains=value) |
            Q(genre__icontains=value)
        )

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="search")
    def search_books(self, request):
        search_query = request.query_params.get("search", "").strip()

        # Check if the search query is empty
        if not search_query:
            return Response(
                {"error": "Please provide a search info."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Apply filtering using BookFilter
        book_filter = BookFilter({'search': search_query}, queryset=self.get_queryset())
        filtered_queryset = book_filter.qs

        if filtered_queryset.exists():
            # Record search history
            PreviousSearch.objects.create(
                user=request.user, query=search_query
            )

            serializer = BookSerializer(filtered_queryset, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)

        return Response(
            {"error": "No results found for the provided search query."},
            status=status.HTTP_404_NOT_FOUND,
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
