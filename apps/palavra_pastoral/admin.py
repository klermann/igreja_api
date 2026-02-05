from django.contrib import admin
from .models import PalavraPastoral

@admin.register(PalavraPastoral)
class PalavraPastoralAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor_nome", "publicado_em", "publicado", "plataforma", "views_count", "shares_count", "ordem")
    list_filter = ("publicado", "plataforma", "autor_nome")
    search_fields = ("titulo", "autor_nome", "tema", "descricao", "video_url")
    ordering = ("-publicado_em", "ordem")
    readonly_fields = ("views_count", "shares_count", "created_at", "updated_at", "slug")
