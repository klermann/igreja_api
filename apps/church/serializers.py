from django.db import transaction
from rest_framework import serializers

from .models import (
    Church,
    Congregation,
    CongregationLocation,
    CongregationImages,
    CongregationDetails,
    CongregationContact,
    CongregationEvaluation,
)


class ChurchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Church
        fields = ("id", "name", "slug", "city", "state", "is_active")


class CongregationLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongregationLocation
        fields = ("latitude", "longitude", "altitude")


class CongregationImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongregationImages
        fields = ("imagem_estatica", "imagem_streetview", "galeria_imagens", "thumbnail")


class CongregationDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongregationDetails
        fields = (
            "tipo_local",
            "descricao",
            "ponto_referencia",
            "horario_funcionamento",
            "acessibilidade",
            "estacionamento",
        )


class CongregationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongregationContact
        fields = ("telefone", "email", "redes_sociais")


class CongregationEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CongregationEvaluation
        fields = ("nota_media", "numero_avaliacoes", "comentarios")


class CongregationSerializer(serializers.ModelSerializer):
    # PT-BR (igual seu JSON) mapeando pro model
    nome = serializers.CharField(source="name")
    endereco = serializers.CharField(source="address", required=False, allow_blank=True)
    cidade = serializers.CharField(source="city", required=False, allow_blank=True)
    estado = serializers.CharField(source="state", required=False, allow_blank=True)

    localizacao = CongregationLocationSerializer(source="location", required=False, allow_null=True)
    imagens = CongregationImagesSerializer(source="images", required=False, allow_null=True)
    detalhes = CongregationDetailsSerializer(source="details", required=False, allow_null=True)
    contato = CongregationContactSerializer(source="contact", required=False, allow_null=True)
    avaliacao = CongregationEvaluationSerializer(source="evaluation", required=False, allow_null=True)

    class Meta:
        model = Congregation
        fields = (
            "id",
            "church",
            "slug",
            "nome",
            "endereco",
            "cep",
            "cidade",
            "estado",
            "status",
            "is_active",
            "localizacao",
            "imagens",
            "detalhes",
            "contato",
            "avaliacao",
        )

    def _upsert_o2o(self, instance, model_cls, data):
        if data is None:
            return
        model_cls.objects.update_or_create(congregation=instance, defaults=data)

    @transaction.atomic
    def create(self, validated_data):
        location = validated_data.pop("location", None)
        images = validated_data.pop("images", None)
        details = validated_data.pop("details", None)
        contact = validated_data.pop("contact", None)
        evaluation = validated_data.pop("evaluation", None)

        obj = super().create(validated_data)

        self._upsert_o2o(obj, CongregationLocation, location)
        self._upsert_o2o(obj, CongregationImages, images)
        self._upsert_o2o(obj, CongregationDetails, details)
        self._upsert_o2o(obj, CongregationContact, contact)
        self._upsert_o2o(obj, CongregationEvaluation, evaluation)

        return obj

    @transaction.atomic
    def update(self, instance, validated_data):
        location = validated_data.pop("location", None)
        images = validated_data.pop("images", None)
        details = validated_data.pop("details", None)
        contact = validated_data.pop("contact", None)
        evaluation = validated_data.pop("evaluation", None)

        obj = super().update(instance, validated_data)

        self._upsert_o2o(obj, CongregationLocation, location)
        self._upsert_o2o(obj, CongregationImages, images)
        self._upsert_o2o(obj, CongregationDetails, details)
        self._upsert_o2o(obj, CongregationContact, contact)
        self._upsert_o2o(obj, CongregationEvaluation, evaluation)

        return obj
