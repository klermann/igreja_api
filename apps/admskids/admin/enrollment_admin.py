from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ("kid", "kids_class", "start_date", "end_date", "is_active")
    list_filter = ("is_active", "kids_class")
    search_fields = ("kid__first_name", "kid__last_name", "kids_class__name")
    autocomplete_fields = ("kid", "kids_class")
