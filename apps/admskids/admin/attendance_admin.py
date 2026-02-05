from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import KidAttendance


@admin.register(KidAttendance)
class KidAttendanceAdmin(ModelAdmin):
    list_display = ("kid", "session", "status", "checkin_at", "checkout_at")
    list_filter = ("status",)
    search_fields = ("kid__first_name", "kid__last_name", "session__kids_class__name")
    autocomplete_fields = ("kid", "session")
    readonly_fields = ("checkin_at", "checkout_at")
