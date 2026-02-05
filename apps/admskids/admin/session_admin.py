from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import ClassSession, KidAttendance


class AttendanceInline(admin.TabularInline):
    model = KidAttendance
    extra = 0
    autocomplete_fields = ("kid",)
    readonly_fields = ("checkin_at", "checkout_at")
    fields = ("kid", "status", "checkin_at", "checkout_at", "picked_up_by", "notes")


@admin.register(ClassSession)
class ClassSessionAdmin(ModelAdmin):
    list_display = ("kids_class", "date", "created_by")
    list_filter = ("kids_class", "date")
    search_fields = ("kids_class__name",)
    autocomplete_fields = ("kids_class", "created_by")
    inlines = (AttendanceInline,)
