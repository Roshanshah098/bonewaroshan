# from django.contrib import admin
# from .models import Genre, Book, PreviousSearch,Poem, Story, Question, Perception, Information, Comment

# # Register your models here.

# # << ::: for content :::>>
# @admin.register(Poem)
# class PoemAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "created_at", "updated_at")
#     search_fields = ("title", "author__username")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)

# @admin.register(Story)
# class StoryAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "created_at", "updated_at")
#     search_fields = ("title", "author__username")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)

# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "created_at", "updated_at")
#     search_fields = ("title", "author__username")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)

# @admin.register(Perception)
# class PerceptionAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "created_at", "updated_at")
#     search_fields = ("title", "author__username")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)

# @admin.register(Information)
# class InformationAdmin(admin.ModelAdmin):
#     list_display = ("title", "author", "created_at", "updated_at")
#     search_fields = ("title", "author__username")
#     list_filter = ("created_at", "updated_at")
#     ordering = ("-created_at",)


# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ("user", "comment_text", "content_type", "object_id", "parent")
#     search_fields = ("user__username", "comment_text")
#     list_filter = ("content_type", "user")
#     ordering = ("-id",)

#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user', 'content_type', 'parent')
