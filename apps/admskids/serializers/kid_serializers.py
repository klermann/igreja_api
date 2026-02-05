from rest_framework import serializers

from ..models import Enrollment, Guardian, Kid, KidGuardian


class GuardianMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = ("id", "name", "email", "phone", "relationship")


class EnrollmentMiniSerializer(serializers.ModelSerializer):
    kids_class_name = serializers.CharField(source="kids_class.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "kids_class", "kids_class_name", "start_date", "end_date", "is_active")


class KidSerializer(serializers.ModelSerializer):
    guardians = serializers.SerializerMethodField()
    enrollments = EnrollmentMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Kid
        fields = (
            "id",
            "congregation",
            "first_name",
            "last_name",
            "birth_date",
            "gender",
            "allergies",
            "medical_notes",
            "notes",
            "photo",
            "is_active",
            "guardians",
            "enrollments",
        )

    def get_guardians(self, obj):
        qs = Guardian.objects.filter(guardian_kids__kid=obj, is_active=True).distinct()
        return GuardianMiniSerializer(qs, many=True).data


class KidWriteSerializer(serializers.ModelSerializer):
    guardian_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Kid
        fields = (
            "id",
            "congregation",
            "first_name",
            "last_name",
            "birth_date",
            "gender",
            "allergies",
            "medical_notes",
            "notes",
            "photo",
            "is_active",
            "guardian_ids",
        )

    def create(self, validated_data):
        guardian_ids = validated_data.pop("guardian_ids", [])
        kid = super().create(validated_data)
        self._sync_guardians(kid, guardian_ids)
        return kid

    def update(self, instance, validated_data):
        guardian_ids = validated_data.pop("guardian_ids", None)
        kid = super().update(instance, validated_data)
        if guardian_ids is not None:
            self._sync_guardians(kid, guardian_ids)
        return kid

    def _sync_guardians(self, kid: Kid, guardian_ids: list[int]):
        # Replace links (simple + predictable for the app)
        KidGuardian.objects.filter(kid=kid).exclude(guardian_id__in=guardian_ids).delete()
        existing = set(KidGuardian.objects.filter(kid=kid).values_list("guardian_id", flat=True))
        to_create = [gid for gid in guardian_ids if gid not in existing]
        KidGuardian.objects.bulk_create([KidGuardian(kid=kid, guardian_id=gid) for gid in to_create])
