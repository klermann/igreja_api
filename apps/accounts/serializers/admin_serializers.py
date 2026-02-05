from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Role

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "code", "name", "priority", "description", "is_active")


class AdminUserSerializer(serializers.ModelSerializer):
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "congregation",
            "roles",
            "is_active",
            "is_staff",
            "date_joined",
            "updated_at",
        )
        read_only_fields = ("date_joined", "updated_at")
