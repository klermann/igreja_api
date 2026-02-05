from rest_framework import serializers
from .models import PalavraPastoral

class PalavraPastoralSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    capa_url = serializers.SerializerMethodField()

    class Meta:
        model = PalavraPastoral
        fields = [
            "id", "slug", "titulo", "tema",
            "autor_nome", "autor_cargo",
            "publicado_em", "descricao",
            "video_url", "plataforma", "duracao_segundos",
            "thumbnail_url", "capa_url",
            "views_count", "shares_count",
        ]

    def _abs(self, request, file_field):
        if not file_field:
            return None
        url = file_field.url
        return request.build_absolute_uri(url) if request else url

    def get_thumbnail_url(self, obj):
        request = self.context.get("request")
        return self._abs(request, obj.thumbnail)

    def get_capa_url(self, obj):
        request = self.context.get("request")
        return self._abs(request, obj.capa)
