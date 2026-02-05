from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AoVivoCategoryViewSet, AoVivoVideoViewSet

router = DefaultRouter()
router.register(r"categories", AoVivoCategoryViewSet, basename="aovivo-categories")
router.register(r"videos", AoVivoVideoViewSet, basename="aovivo-videos")

urlpatterns = [
    path("", include(router.urls)),
]
