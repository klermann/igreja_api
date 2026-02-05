from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import F

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter

from .models import PalavraPastoral
from .serializers import PalavraPastoralSerializer


@extend_schema_view(
    list=extend_schema(tags=["Palavra pastoral"]),
    retrieve=extend_schema(tags=["Palavra pastoral"]),
    increment_view=extend_schema(tags=["Palavra pastoral"]),
    increment_share=extend_schema(tags=["Palavra pastoral"]),
)
class PalavraPastoralViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = PalavraPastoralSerializer

    def get_queryset(self):
        return PalavraPastoral.objects.filter(publicado=True).order_by("-publicado_em", "ordem", "-id")

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, pk=None):
        PalavraPastoral.objects.filter(pk=pk).update(views_count=F("views_count") + 1)
        return response.Response({"ok": True}, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.AllowAny])
    def increment_share(self, request, pk=None):
        PalavraPastoral.objects.filter(pk=pk).update(shares_count=F("shares_count") + 1)
        return response.Response({"ok": True}, status=status.HTTP_200_OK)
