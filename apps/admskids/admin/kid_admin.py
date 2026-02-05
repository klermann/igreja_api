from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import Enrollment, Kid, KidGuardian, KidAttendance


class KidGuardianInline(admin.TabularInline):
    model = KidGuardian
    extra = 0
    autocomplete_fields = ("guardian",)


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ("kids_class",)


class AttendanceInline(admin.TabularInline):
    model = KidAttendance
    extra = 0
    autocomplete_fields = ("session",)
    readonly_fields = ("checkin_at", "checkout_at")


@admin.register(Kid)
class KidAdmin(ModelAdmin):
    list_display = ("first_name", "last_name", "congregation", "birth_date", "is_active")
    list_filter = ("is_active", "congregation", "gender")
    search_fields = ("first_name", "last_name")
    autocomplete_fields = ("congregation",)
    inlines = (KidGuardianInline, EnrollmentInline, AttendanceInline)
