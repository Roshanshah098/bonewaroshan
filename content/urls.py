from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ContentViewSet

router = DefaultRouter()
router.register(r"content", ContentViewSet, basename="content")

urlpatterns = [
    path("api/", include(router.urls)),
]
