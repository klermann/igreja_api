from rest_framework import serializers

from ..models import User


class UserMeSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    congregation_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name", "email", "roles", "congregation_name")

    def get_roles(self, obj: User):
        return obj.role_codes

    def get_congregation_name(self, obj: User):
        return obj.congregation_name
