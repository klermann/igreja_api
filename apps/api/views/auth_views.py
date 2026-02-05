from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from apps.accounts.models import PasswordResetToken
from apps.accounts.serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserMeSerializer,
)
from apps.accounts.services.password_reset_service import send_password_reset_email

from ..throttles import ForgotPasswordThrottle, LoginThrottle, ResetPasswordThrottle

User = get_user_model()


@extend_schema(tags=["Auth"])
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_classes = [LoginThrottle]


@extend_schema(tags=["Auth"])
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)


@extend_schema(tags=["Auth"])
class ForgotPasswordView(APIView):
    """Basic stub endpoint.

    You can later integrate with email provider.
    Always respond 200 to avoid leaking registered emails.
    """

    permission_classes = [permissions.AllowAny]
    throttle_classes = [ForgotPasswordThrottle]

    def post(self, request):
        ser = ForgotPasswordSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)
        email = ser.validated_data["email"].strip().lower()

        # Do not leak whether the email exists
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            raw_token, token_obj = PasswordResetToken.create_for_user(
                user,
                ttl_minutes=30,
                ip=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            # You can switch to an email provider later; dev uses console backend.
            send_password_reset_email(to_email=user.email, raw_token=raw_token)

        return Response(
            {"detail": "If the email exists, reset instructions were sent."},
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=["Auth"])
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ResetPasswordThrottle]

    def post(self, request):
        ser = ResetPasswordSerializer(data=request.data or {})
        ser.is_valid(raise_exception=True)
        raw_token = ser.validated_data["token"]

        token_hash = PasswordResetToken.hash_token(raw_token)
        token_obj = (
            PasswordResetToken.objects.select_related("user")
            .filter(token_hash=token_hash, used_at__isnull=True, expires_at__gt=timezone.now())
            .first()
        )

        if not token_obj:
            return Response({"detail": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        password = ser.validated_data["new_password"]
        # Validate password against Django's built-in validators
        password_validation.validate_password(password, user=user)
        user.set_password(password)
        user.save(update_fields=["password"])
        token_obj.mark_used()

        return Response({"detail": "Senha atualizada com sucesso."}, status=status.HTTP_200_OK)
