from rest_framework import serializers
from .models import AoVivoCategory, AoVivoVideo


class AoVivoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AoVivoCategory
        fields = ["id", "name", "slug", "description", "order", "is_active"]


class AoVivoVideoSerializer(serializers.ModelSerializer):
    category = AoVivoCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = AoVivoVideo
        fields = [
            "id",
            "category",
            "category_id",
            "title",
            "subtitle",
            "provider",
            "video_url",
            "thumbnail_url",
            "published_at",
            "order",
            "is_active",
        ]
