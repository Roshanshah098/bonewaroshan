from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count
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


# for search, book must require as to maintain the info for the book;
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

    title = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Book Title"
    )
    author = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Author Name"
    )
    genre = models.CharField(
        max_length=100,
        choices=genre_choices,
        null=True,
        blank=True,
        verbose_name="Genre",
    )
    description = models.TextField(
        null=True, blank=True, verbose_name="Book Description"
    )
    published_date = models.DateField(
        null=True, blank=True, verbose_name="Date Published"
    )
    rating = models.PositiveSmallIntegerField(
        default=0, null=False, blank=False, verbose_name="Book Rating"
    )
    categories = models.CharField(
        max_length=100,
        choices=MEDIA_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Media Type",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return self.title

    @property
    def is_trending(self):
        trending_rating_threshold = 4.0
        recent_time_threshold = timezone.now() - timedelta(days=180)  # 6 months
        one_week_ago = timezone.now() - timedelta(days=7)
        views_last_week = self.views.filter(view_date__gte=one_week_ago).count()
        return self.rating >= trending_rating_threshold and (
            self.published_date >= recent_time_threshold.date()
            or views_last_week >= 10000
        )

    @classmethod
    def get_popular_books(cls):
        return (
            cls.objects.annotate(num_views=Count("views"))
            .filter(rating__gte=4.0)
            .order_by("-rating", "-num_views")
        )


class BookView(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="views")
    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="book_views",
        null=True,
        blank=True,
    )
    view_date = models.DateTimeField(default=timezone.now, verbose_name="View Date")


class PreviousSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User")
    query = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Search Query"
    )
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name="Searched At")

    def __str__(self):
        return f"Search by {self.user.username} at {self.searched_at}: {self.query}"
