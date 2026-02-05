from rest_framework.routers import DefaultRouter

from .api_views import ChurchViewSet, CongregationViewSet

router = DefaultRouter()
router.register(r"churches", ChurchViewSet, basename="church")
router.register(r"congregations", CongregationViewSet, basename="congregation")

urlpatterns = router.urls
