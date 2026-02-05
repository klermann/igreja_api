from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from drf_spectacular.utils import extend_schema

from .models import Role
from .serializers.admin_serializers import AdminUserSerializer, RoleSerializer

User = get_user_model()


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


@extend_schema(tags=["Contas"])
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsStaff]


@extend_schema(tags=["Contas"])
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("congregation").prefetch_related("roles").all()
    serializer_class = AdminUserSerializer
    permission_classes = [IsStaff]
