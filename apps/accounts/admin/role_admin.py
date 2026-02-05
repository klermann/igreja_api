from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import Role


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "code", "priority", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code")
    ordering = ("priority", "code")
