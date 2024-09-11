from rest_framework import serializers
from .models import Genre, Book, PreviousSearch


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"


class PreviousSearchSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PreviousSearch
        fields = ["id", "user", "query", "searched_at"]

    def validate_query(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Search query cannot be empty.")
        return value

