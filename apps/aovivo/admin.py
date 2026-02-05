from django.contrib import admin
from .models import AoVivoCategory, AoVivoVideo


class AoVivoVideoInline(admin.TabularInline):
    model = AoVivoVideo
    extra = 0
    fields = ("title", "provider", "video_url", "published_at", "order", "is_active")
    ordering = ("order", "-published_at", "-created_at")
    show_change_link = True


@admin.register(AoVivoCategory)
class AoVivoCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    inlines = [AoVivoVideoInline]


@admin.register(AoVivoVideo)
class AoVivoVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "provider", "published_at", "order", "is_active")
    list_filter = ("provider", "is_active", "category")
    search_fields = ("title", "subtitle", "video_url", "category__name")
    ordering = ("-published_at", "-created_at", "order")
    autocomplete_fields = ("category",)
