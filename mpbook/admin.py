from django.contrib import admin
from .models import Genre, Book, PreviousSearch, BookView

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
        "categories",
        "published_date",
        "rating",
        "is_trending_display",  
    )
    search_fields = ("title", "author", "genre", "categories")
    list_filter = (
        "genre",
        "categories",
        "published_date",
        "rating",
    )
    ordering = ("-published_date", "-rating")  
    
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
    )
    list_filter = ("searched_at",)
    ordering = ("-searched_at",)

@admin.register(BookView)
class BookViewAdmin(admin.ModelAdmin):
    list_display = ("book", "viewer", "view_date")
    search_fields = (
        "book__title",
        "viewer__username",
        "viewer__email", 
    )
    list_filter = ("view_date",)
    ordering = ("-view_date",)
