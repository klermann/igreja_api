from rest_framework.routers import DefaultRouter

from .api_views import RoleViewSet, UserViewSet

router = DefaultRouter()
router.register(r"roles", RoleViewSet, basename="accounts_role")
router.register(r"users", UserViewSet, basename="accounts_user")

urlpatterns = router.urls
