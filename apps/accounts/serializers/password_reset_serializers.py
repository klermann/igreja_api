from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if len(attrs.get("token", "")) < 20:
            raise serializers.ValidationError({"token": _("Token inválido.")})
        return attrs