from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    GENRE_CHOICES = [
        ("History", "History"),
        ("Biography", "Biography"),
        ("Fantasy", "Fantasy"),
        ("Philosophy", "Philosophy"),
        ("Engineering", "Engineering"),
        ("Technology", "Technology"),
        ("Sports", "Sports"),
        ("Music", "Music"),
        ("Drama", "Drama"),
        ("Patriotic", "Patriotic"),
    ]

    name = models.CharField(max_length=50, choices=GENRE_CHOICES, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    genre_choices = [
        ("Fiction", "Fiction"),
        ("Non-Fiction", "Non-Fiction"),
        ("Mystery", "Mystery"),
        ("Science Fiction", "Science Fiction"),
        ("Biography", "Biography"),
        ("Fantasy", "Fantasy"),
        ("History", "History"),
        ("Poetry", "Poetry"),
    ]

    MEDIA_TYPE_CHOICES = [
        ("Book", "Book"),
        ("Audio", "Audio"),
        ("Ebook", "Ebook"),
        ("Book & Audio", "Book & Audio"),
    ]

    title = models.CharField(max_length=255, null=False, blank=False)
    author = models.CharField(max_length=255, null=False, blank=False)
    genre = models.CharField(
        max_length=100, choices=genre_choices, null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=0, null=False, blank=False)
    categories = models.CharField(
        max_length=100, choices=MEDIA_TYPE_CHOICES, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_trending(self):
        trending_rating_threshold = 4.0
        recent_time_threshold = timezone.now() - timedelta(days=180)  # 6 months
        popular_search_count = PreviousSearch.objects.filter(
            query__icontains=self.title
        ).count()
        return self.rating >= trending_rating_threshold and (
            self.published_date >= recent_time_threshold.date()
            or popular_search_count >= 100
        )

    # Annotate based on search count and filter by rating
    @classmethod
    def get_popular_books(cls):
        return (
            cls.objects.annotate(search_count=Count("previoussearch__query"))
            .filter(rating__gte=4.0)
            .order_by("-rating", "-search_count")
        )


class PreviousSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255, null=False, blank=False)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user.username} at {self.searched_at}: {self.query}"
