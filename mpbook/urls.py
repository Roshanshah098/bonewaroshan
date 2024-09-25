from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenreViewSet, BookViewSet

router = DefaultRouter()
router.register(r"genres", GenreViewSet, basename="genre")
router.register(r"books", BookViewSet, basename="book")

urlpatterns = [
    path("mp/", include(router.urls)),
]
