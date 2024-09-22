from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.db.models import Q
from .models import Genre, Book, PreviousSearch, BookView
from .serializers import GenreSerializer, BookSerializer, PreviousSearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from .filters import GenreFilter, BookFilter
from .paginations import CustomPagination


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

    @action(detail=False, methods=["get"], url_path="trending")
    def trending_books(self, request):
        trending_books = Book.objects.filter(is_trending=True)
        if not trending_books.exists():
            return Response(
                {"detail": "No trending books found."}, status=status.HTTP_404_NOT_FOUND
            )

        page = self.paginate_queryset(trending_books)
        serializer = (
            self.get_serializer(page, many=True)
            if page
            else self.get_serializer(trending_books, many=True)
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=["get"], url_path="recent-searches")
    def recent_searches(self, request):
        recent_searches = PreviousSearch.objects.filter(user=request.user).order_by(
            "-searched_at"
        )[:10]
        serializer = PreviousSearchSerializer(recent_searches, many=True)
        return Response({"recent_searches": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="rate")
    def rate_book(self, request, pk=None):
        book = self.get_object()
        rating = request.data.get("rating")

        # Create a dictionary for rating update
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

    @action(detail=True, methods=["post"], url_path="view")
    def record_view(self, request, pk=None):
        book = self.get_object()
        viewer = request.user
        try:
            BookView.objects.create(book=book, viewer=viewer, view_date=timezone.now())
            book.views += 1
            book.save()
            return Response({"status": "Book view recorded"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["delete"], url_path="clear-history")
    def clear_search_history(self, request):
        previous_searches = PreviousSearch.objects.filter(user=request.user)
        previous_searches.delete()
        return Response(
            {"detail": "Search history cleared."}, status=status.HTTP_204_NO_CONTENT
        )
