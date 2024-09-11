from django.contrib import admin
from .models import Genre, Book, PreviousSearch


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "id")
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "genre",
        "published_date",
        "rating",
        "is_trending_display",  # Display the trending status
    )
    search_fields = ("title", "author", "genre")
    list_filter = (
        "genre",
        "published_date",
    )
    ordering = ("-published_date",)
    readonly_fields = ("is_trending_display",)

    # Custom method to display is_trending in the admin
    def is_trending_display(self, obj):
        return obj.is_trending

    is_trending_display.short_description = "Trending"
    is_trending_display.boolean = True  # Show True/False as icons


@admin.register(PreviousSearch)
class PreviousSearchAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "searched_at")
    search_fields = (
        "user__username",
        "user__email",
        "query",
    )  # Searching by username and email
    list_filter = ("searched_at",)
    ordering = ("-searched_at",)
