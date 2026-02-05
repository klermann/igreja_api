from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import ClassSession, Enrollment, KidsClass


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ("kid",)


class SessionInline(admin.TabularInline):
    model = ClassSession
    extra = 0
    fields = ("date", "created_by")
    autocomplete_fields = ("created_by",)


@admin.register(KidsClass)
class KidsClassAdmin(ModelAdmin):
    list_display = ("name", "congregation", "age_min", "age_max", "is_active")
    list_filter = ("is_active", "congregation")
    search_fields = ("name",)
    autocomplete_fields = ("congregation",)
    inlines = (EnrollmentInline, SessionInline)
