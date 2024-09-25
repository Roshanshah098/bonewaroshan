from django.db import models
from django.utils import timezone

# from django.db.models import Count, Q, OuterRef, Subquery
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


# Base content creation using abstarct
class AbstractContent(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_authors",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class Poem(AbstractContent):
    thumbnail = models.ImageField(upload_to="images/poem/", null=True, blank=True)


class Story(AbstractContent):
    thumbnail = models.ImageField(upload_to="images/story/", null=True, blank=True)


class Question(AbstractContent):
    thumbnail = models.ImageField(upload_to="images/question/", null=True, blank=True)


class Perception(AbstractContent):
    pass


class Information(AbstractContent):
    thumbnail = models.ImageField(
        upload_to="images/informational/", null=True, blank=True
    )


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment_text = models.TextField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name="comments"
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )

    def __str__(self):
        return f"{self.user.username} - {self.comment_text[:25]}"
