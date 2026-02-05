from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from ..models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "name", "get_congregation", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "roles")
    search_fields = ("email", "name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Dados", {"fields": ("name", "congregation", "roles")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    readonly_fields = ("date_joined",)

    def get_congregation(self, obj: User):
        return obj.congregation.name if obj.congregation else "-"

    get_congregation.short_description = "Congregação"
