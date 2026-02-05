from rest_framework import permissions, viewsets
from drf_spectacular.utils import extend_schema

from .models import Church, Congregation
from .serializers import ChurchSerializer, CongregationSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_staff


@extend_schema(tags=["Igreja"])
class ChurchViewSet(viewsets.ModelViewSet):
    queryset = Church.objects.all()
    serializer_class = ChurchSerializer
    permission_classes = [IsStaffOrReadOnly]


@extend_schema(tags=["Igreja"])
class CongregationViewSet(viewsets.ModelViewSet):
    serializer_class = CongregationSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = (
            Congregation.objects
            .select_related(
                "church",
                "location",
                "images",
                "details",
                "contact",
                "evaluation",
            )
            .all()
        )

        church_id = self.request.query_params.get("church")
        if church_id:
            qs = qs.filter(church_id=church_id)

        return qs
