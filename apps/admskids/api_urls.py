from rest_framework.routers import DefaultRouter

from .views.api_views import (
    ClassSessionViewSet,
    EnrollmentViewSet,
    GuardianViewSet,
    KidAttendanceViewSet,
    KidViewSet,
    KidsClassViewSet,
)

router = DefaultRouter()
router.register(r"kids", KidViewSet, basename="admskids_kid")
router.register(r"guardians", GuardianViewSet, basename="admskids_guardian")
router.register(r"classes", KidsClassViewSet, basename="admskids_class")
router.register(r"enrollments", EnrollmentViewSet, basename="admskids_enrollment")
router.register(r"sessions", ClassSessionViewSet, basename="admskids_session")
router.register(r"attendances", KidAttendanceViewSet, basename="admskids_attendance")

urlpatterns = router.urls
