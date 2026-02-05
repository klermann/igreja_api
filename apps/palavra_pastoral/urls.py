from rest_framework.routers import DefaultRouter
from .views import PalavraPastoralViewSet

router = DefaultRouter()
router.register(r"palavra-pastoral", PalavraPastoralViewSet, basename="palavra-pastoral")
urlpatterns = router.urls
