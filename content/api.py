from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from .models import Poem, Story, Question, Perception, Information, Comment
from .serializers import (
    PoemSerializer,
    StorySerializer,
    QuestionSerializer,
    PerceptionSerializer,
    InformationSerializer,
    CommentSerializer,
)


class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_mapping = {
        "poem": PoemSerializer,
        "story": StorySerializer,
        "question": QuestionSerializer,
        "perception": PerceptionSerializer,
        "information": InformationSerializer,
    }

    def get_serializer_class(self):
        content_type = self.request.query_params.get("content_type")
        if not content_type:
            raise ValidationError("Content type is required.")

        serializer_class = self.serializer_mapping.get(content_type.lower())
        if serializer_class is None:
            raise ValidationError(f"Invalid content type: {content_type}.")
        return serializer_class

    def get_queryset(self):
        content_type = self.request.query_params.get("content_type")
        if not content_type:
            raise ValidationError("Content type is required.")

        model_mapping = {
            "poem": Poem,
            "story": Story,
            "question": Question,
            "perception": Perception,
            "information": Information,
        }
        model_class = model_mapping.get(content_type.lower())
        if model_class is None:
            raise ValidationError(f"Invalid content type: {content_type}.")
        return model_class.objects.all()

    @action(detail=False, methods=["post"], url_path="create-content")
    def create_content(self, request):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="add-comment")
    def add_comment(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # List all comments or filter by content type and object ID.
    @action(detail=False, methods=["get"], url_path="list-comments")
    def list_comments(self, request):
        content_type = request.query_params.get("content_type")
        object_id = request.query_params.get("object_id")

        if content_type and object_id:
            content_type_instance = ContentType.objects.get(model=content_type)
            comments = Comment.objects.filter(
                content_type=content_type_instance, object_id=object_id
            )
        else:
            comments = Comment.objects.all()

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
