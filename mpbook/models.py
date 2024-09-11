from django.db import models
from datetime import timedelta
from django.utils import timezone

from django.conf import (
    settings,
)  # (# For referring to the custom user model dynamically)


# as first, interest must be selected in order to proceed;
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
    rating = models.FloatField( 
        default=0.0, null=False, blank=False, verbose_name="Book Rating"  
    )  
    views = models.IntegerField(
        default=0, null=False, blank=False, verbose_name="View Count"   
    )  
    categories = models.CharField(max_length=100, choices=MEDIA_TYPE_CHOICES, null=True, blank=True, verbose_name="Media Type")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At") 

    def __str__(self):
        return self.title

    @property
    def is_trending(self):
        """
        Determines if the book is trending based on certain criteria like:
        - High rating (just eg: above 4.0)
        - High number of views in the last week
        - Recent publication (last 6 months)
        """
        trending_rating_threshold = 4.0
        recent_view_threshold = 10000
        recent_time_threshold = timezone.now() - timedelta(
            days=180
        )  # for now, 6 months

        # Check if the book is trending based on rating, views, and publication date
        is_highly_rated = self.rating >= trending_rating_threshold
        is_recent = (
            self.published_date and self.published_date >= recent_time_threshold.date()
        )
        has_high_views = self.views >= recent_view_threshold

        # A book is trending if it meets the rating and one of the other criteria
        return is_highly_rated and (is_recent or has_high_views)

    # Returns the list of popular books based on rating and views.
    @classmethod
    def get_popular_books(cls):
        return cls.objects.filter(rating__gte=4.0).order_by("-rating", "-views")


class PreviousSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User"
    )
    query = models.CharField(
        max_length=255, null=False, blank=False, verbose_name="Search Query"
    )
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name="Searched At")

    def __str__(self):
        return f"Search by {self.user.username} at {self.searched_at}: {self.query}"
