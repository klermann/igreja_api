from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AoVivoCategory, AoVivoVideo
from .serializers import AoVivoCategorySerializer, AoVivoVideoSerializer


class AoVivoCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/aovivo/categories/
    GET /api/aovivo/categories/{id}/
    GET /api/aovivo/categories/{id}/videos/
    """
    permission_classes = [AllowAny]
    serializer_class = AoVivoCategorySerializer

    def get_queryset(self):
        qs = AoVivoCategory.objects.all()
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=(active.lower() in ["1", "true", "yes"]))
        return qs.order_by("order", "name")

    @action(detail=True, methods=["get"], url_path="videos")
    def videos(self, request, pk=None):
        category = self.get_object()
        qs = category.videos.all()

        active = request.query_params.get("active")
        if active is None:
            qs = qs.filter(is_active=True)
        else:
            qs = qs.filter(is_active=(active.lower() in ["1", "true", "yes"]))

        # ordenação padrão do model já ajuda, mas mantemos explícito:
        qs = qs.order_by("-published_at", "-created_at", "order")

        return Response(AoVivoVideoSerializer(qs, many=True).data)


class AoVivoVideoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/aovivo/videos/?category_id=1
    GET /api/aovivo/videos/?category_slug=culto-de-ensino
    """
    permission_classes = [AllowAny]
    serializer_class = AoVivoVideoSerializer

    def get_queryset(self):
        qs = AoVivoVideo.objects.select_related("category").all()

        # Por padrão: só ativos
        active = self.request.query_params.get("active")
        if active is None:
            qs = qs.filter(is_active=True)
        else:
            qs = qs.filter(is_active=(active.lower() in ["1", "true", "yes"]))

        category_id = self.request.query_params.get("category_id")
        if category_id:
            qs = qs.filter(category_id=category_id)

        category_slug = self.request.query_params.get("category_slug")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        return qs.order_by("-published_at", "-created_at", "order")
