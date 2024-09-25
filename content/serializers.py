from rest_framework import serializers
from .models import Poem, Story, Question, Perception, Information, Comment
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class PoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poem
        fields = "__all__"


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = "__all__"


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class PerceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perception
        fields = "__all__"


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    content_type = serializers.SlugRelatedField(
        slug_field="model", queryset=ContentType.objects.all()
    )

    class Meta:
        model = Comment
        fields = "__all__"

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return None

    def create(self, validated_data):
        content_type = validated_data.pop("content_type")
        object_id = validated_data.pop("object_id")
        comment = Comment.objects.create(
            content_type=content_type, object_id=object_id, **validated_data
        )
        return comment
