from django.contrib import admin
from unfold.admin import ModelAdmin

from ..models import (
    Congregation,
    CongregationLocation,
    CongregationImages,
    CongregationDetails,
    CongregationContact,
    CongregationEvaluation,
)


class _BaseOneToOneInline(admin.StackedInline):
    extra = 0
    max_num = 1
    can_delete = True
    show_change_link = True


class CongregationLocationInline(_BaseOneToOneInline):
    model = CongregationLocation


class CongregationImagesInline(_BaseOneToOneInline):
    model = CongregationImages


class CongregationDetailsInline(_BaseOneToOneInline):
    model = CongregationDetails


class CongregationContactInline(_BaseOneToOneInline):
    model = CongregationContact


class CongregationEvaluationInline(_BaseOneToOneInline):
    model = CongregationEvaluation


@admin.register(Congregation)
class CongregationAdmin(ModelAdmin):
    list_display = ("name", "church", "slug", "city", "state", "cep", "status", "is_active")
    list_filter = ("status", "is_active", "state", "church")
    search_fields = ("name", "slug", "church__name", "city", "cep")
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        ("Identificação", {"fields": ("church", "name", "slug")}),
        ("Endereço", {"fields": ("address", "cep", "city", "state")}),
        ("Status", {"fields": ("status", "is_active")}),
    )

    inlines = [
        CongregationLocationInline,
        CongregationImagesInline,
        CongregationDetailsInline,
        CongregationContactInline,
        CongregationEvaluationInline,
    ]
