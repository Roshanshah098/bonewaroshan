from rest_framework import serializers
from .models import Genre, Book, PreviousSearch,BookView
from django.conf import settings

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        
    def to_internal_value(self, data):  
            #default validation
            validated_data = super().to_internal_value(data)

            #rating is between 1 and 5
            rating = validated_data.get("rating")
            if rating is not None and (rating < 1 or rating > 5):
                raise serializers.ValidationError({"rating": "Rating must be between 1 and 5."})

            return validated_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['username']  

class BookViewSerializer(serializers.ModelSerializer):
    viewer = UserSerializer(read_only=True)  
    book = BookSerializer(read_only=True)  

    class Meta:
        model = BookView
        fields = ["book", "viewer", "view_date"]  

class PreviousSearchSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PreviousSearch
        fields = ["id", "user", "query", "searched_at"]

    def validate_query(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Search query cannot be empty.")
        return value

