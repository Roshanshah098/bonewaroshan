from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Q, Count
from .models import Genre, Book, PreviousSearch
from .serializers import GenreSerializer, BookSerializer, PreviousSearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta
from .filters import GenreFilter, BookFilter
from .paginations import CustomPagination
from django.core.exceptions import ValidationError


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = GenreFilter
    search_fields = ["name"]

    @action(detail=False, methods=["post"], url_path="validate-selection")
    def validate_selection(self, request):
        genre_ids = request.data.get("genre_ids", [])
        if len(genre_ids) < 4:
            return Response(
                {"error": "You must select at least four genres."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_genre_ids = Genre.objects.filter(id__in=genre_ids).values_list(
            "id", flat=True
        )
        if set(genre_ids) != set(valid_genre_ids):
            return Response(
                {"error": "One or more selected genres are invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Selection is valid."}, status=status.HTTP_200_OK)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author", "genre"]
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        search_query = request.GET.get("search", "")
        if search_query:
            PreviousSearch.objects.create(
                user=request.user, query=search_query, searched_at=timezone.now()
            )

        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="trending-books")
    def trending_books(self, request):
        trending_books = Book.get_trending_books()
        page = self.paginate_queryset(trending_books)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(trending_books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="recent-searches")
    def recent_searches(self, request):
        recent_searches = PreviousSearch.objects.filter(user=request.user).order_by(
            "-searched_at"
        )[:10]
        if not recent_searches.exists():
            return Response(
                {"detail": "No recent searches found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PreviousSearchSerializer(recent_searches, many=True)
        return Response({"recent_searches": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="previous-search-books")
    def previous_search_books(self, request):
        previous_searches = PreviousSearch.objects.filter(user=request.user)

        if not previous_searches.exists():
            return Response(
                {"detail": "No previous searches found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        queries = previous_searches.values_list("query", flat=True)
        book_filter = Q()
        for query in queries:
            search_terms = query.split(",")
            for term in search_terms:
                term = term.strip()
                book_filter |= (
                    Q(title__icontains=term)
                    | Q(author__icontains=term)
                    | Q(genre__exact=term)
                    | Q(categories__exact=term)
                )
        books = Book.objects.filter(book_filter).distinct().order_by("title")[:10]

        if not books.exists():
            return Response(
                {"detail": "No books found based on previous searches."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(books, many=True)
        return Response({"books": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rate")
    def rate_book(self, request, pk=None):
        book = self.get_object()
        rating = request.data.get("rating")
        data = {"rating": rating}

        serializer = self.get_serializer(book, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "Book rating updated",
                    "new_rating": serializer.validated_data.get("rating"),
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["delete"], url_path="clear-history")
    def clear_search_history(self, request):
        previous_searches = PreviousSearch.objects.filter(user=request.user)
        previous_searches.delete()
        return Response(
            {"detail": "Search history cleared."}, status=status.HTTP_204_NO_CONTENT
        )
