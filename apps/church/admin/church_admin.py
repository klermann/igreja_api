from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import Church


@admin.register(Church)
class ChurchAdmin(ModelAdmin):
    list_display = ("name", "slug", "city", "state", "is_active")
    list_filter = ("is_active", "state")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
