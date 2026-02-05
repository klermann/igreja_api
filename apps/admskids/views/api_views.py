from django.db.models import Q
from rest_framework import permissions, viewsets
from drf_spectacular.utils import extend_schema

from ..models import ClassSession, Enrollment, Guardian, Kid, KidAttendance, KidsClass
from ..permissions import IsKidsAdminOrReadOnly, is_kids_admin
from ..serializers import (
    ClassSessionSerializer,
    EnrollmentSerializer,
    GuardianSerializer,
    KidAttendanceSerializer,
    KidSerializer,
    KidWriteSerializer,
    KidsClassSerializer,
)


@extend_schema(tags=["ADMSKIDS"])
class GuardianViewSet(viewsets.ModelViewSet):
    queryset = Guardian.objects.select_related("user").all()
    serializer_class = GuardianSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if is_kids_admin(self.request.user):
            return qs

        # Guardian: vê somente seu próprio registro (user/email)
        u = self.request.user
        return qs.filter(Q(user=u) | Q(email__iexact=u.email)).distinct()


@extend_schema(tags=["ADMSKIDS"])
class KidViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = (
            Kid.objects.select_related("congregation")
            .prefetch_related("enrollments", "kid_guardians")
            .all()
        )
        if is_kids_admin(self.request.user):
            return qs

        # Guardian: vê apenas crianças vinculadas via Guardian.user ou Guardian.email
        u = self.request.user
        return qs.filter(
            Q(kid_guardians__guardian__user=u)
            | Q(kid_guardians__guardian__email__iexact=u.email)
        ).distinct()

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return KidWriteSerializer
        return KidSerializer


@extend_schema(tags=["ADMSKIDS"])
class KidsClassViewSet(viewsets.ModelViewSet):
    queryset = KidsClass.objects.select_related("congregation").all()
    serializer_class = KidsClassSerializer
    permission_classes = [IsKidsAdminOrReadOnly]


@extend_schema(tags=["ADMSKIDS"])
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related("kid", "kids_class").all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if is_kids_admin(self.request.user):
            return qs
        # Guardian: apenas matrículas das suas crianças
        u = self.request.user
        return qs.filter(
            Q(kid__kid_guardians__guardian__user=u)
            | Q(kid__kid_guardians__guardian__email__iexact=u.email)
        ).distinct()


@extend_schema(tags=["ADMSKIDS"])
class ClassSessionViewSet(viewsets.ModelViewSet):
    queryset = ClassSession.objects.select_related("kids_class", "created_by").all()
    serializer_class = ClassSessionSerializer
    permission_classes = [IsKidsAdminOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()


@extend_schema(tags=["ADMSKIDS"])
class KidAttendanceViewSet(viewsets.ModelViewSet):
    queryset = KidAttendance.objects.select_related("session", "kid", "session__kids_class").all()
    serializer_class = KidAttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if is_kids_admin(self.request.user):
            return qs
        # Guardian: só presenças das suas crianças
        u = self.request.user
        return qs.filter(
            Q(kid__kid_guardians__guardian__user=u)
            | Q(kid__kid_guardians__guardian__email__iexact=u.email)
        ).distinct()
