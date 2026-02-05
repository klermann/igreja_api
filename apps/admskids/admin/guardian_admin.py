from django.contrib import admin
from unfold.admin import ModelAdmin
from ..models import Guardian, KidGuardian


class KidInline(admin.TabularInline):
    model = KidGuardian
    extra = 0
    autocomplete_fields = ("kid",)


@admin.register(Guardian)
class GuardianAdmin(ModelAdmin):
    list_display = ("name", "email", "relationship", "user", "is_active")
    list_filter = ("is_active", "relationship")
    search_fields = ("name", "email", "phone")
    autocomplete_fields = ("user",)
    inlines = (KidInline,)
