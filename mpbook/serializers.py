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
        extra_kwargs = {"rating": {"required": False}}

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)
        self.validate_rating(validated_data)
        return validated_data

    def validate_rating(self, validated_data):
        rating = validated_data.get("rating")
        if rating is not None and (rating < 1 or rating > 5):
            raise serializers.ValidationError(
                {"rating": "Rating must be between 1 and 5."}
            )


class PreviousSearchSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PreviousSearch
        fields = ["id", "user", "query", "searched_at"]

    def validate_query(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Search query cannot be empty.")
        return value
