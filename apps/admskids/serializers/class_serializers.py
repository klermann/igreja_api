from rest_framework import serializers

from ..models import ClassSession, Enrollment, KidsClass, KidAttendance


class KidsClassSerializer(serializers.ModelSerializer):
    congregation_name = serializers.CharField(source="congregation.name", read_only=True)

    class Meta:
        model = KidsClass
        fields = ("id", "congregation", "congregation_name", "name", "age_min", "age_max", "is_active")


class EnrollmentSerializer(serializers.ModelSerializer):
    kid_name = serializers.CharField(source="kid.__str__", read_only=True)
    kids_class_name = serializers.CharField(source="kids_class.name", read_only=True)

    class Meta:
        model = Enrollment
        fields = ("id", "kid", "kid_name", "kids_class", "kids_class_name", "start_date", "end_date", "is_active")


class ClassSessionSerializer(serializers.ModelSerializer):
    kids_class_name = serializers.CharField(source="kids_class.name", read_only=True)
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = ClassSession
        fields = ("id", "kids_class", "kids_class_name", "date", "created_by", "created_by_email", "notes")


class KidAttendanceSerializer(serializers.ModelSerializer):
    kid_name = serializers.CharField(source="kid.__str__", read_only=True)
    session_date = serializers.DateField(source="session.date", read_only=True)
    kids_class = serializers.IntegerField(source="session.kids_class_id", read_only=True)

    class Meta:
        model = KidAttendance
        fields = (
            "id",
            "session",
            "session_date",
            "kids_class",
            "kid",
            "kid_name",
            "status",
            "checkin_at",
            "checkout_at",
            "picked_up_by",
            "notes",
        )
