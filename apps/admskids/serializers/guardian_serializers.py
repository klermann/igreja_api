from rest_framework import serializers

from ..models import Guardian


class GuardianSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Guardian
        fields = (
            "id",
            "user",
            "user_email",
            "name",
            "email",
            "phone",
            "relationship",
            "is_active",
        )
