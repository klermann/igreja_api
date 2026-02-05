from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .user_serializers import UserMeSerializer


class LoginSerializer(TokenObtainPairSerializer):
    """JWT login serializer that returns tokens + user payload.

    Response format:
    {
      "tokens": {
        "access": "...",
        "refresh": "...",
        "accessToken": "...",
        "refreshToken": "..."
      },
      "user": {"id", "name", "email", "roles", "congregation_name"}
    }
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Useful custom claims (optional)
        token["email"] = user.email
        token["name"] = user.name
        token["roles"] = user.role_codes
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # SimpleJWT returns {'refresh': '...', 'access': '...'}
        user_data = UserMeSerializer(self.user).data
        tokens = {
            "access": data.get("access"),
            "refresh": data.get("refresh"),
            "accessToken": data.get("access"),
            "refreshToken": data.get("refresh"),
        }
        return {"tokens": tokens, "user": user_data}
