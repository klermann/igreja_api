from django.db import models

from apps.common.fields import EncryptedCharField


class KidAttendance(models.Model):
    """Presença/Check-in por criança em uma sessão."""

    class Status(models.TextChoices):
        PRESENT = "present", "Presente"
        ABSENT = "absent", "Ausente"

    session = models.ForeignKey("admskids.ClassSession", on_delete=models.CASCADE, related_name="attendances")
    kid = models.ForeignKey("admskids.Kid", on_delete=models.CASCADE, related_name="attendances")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    checkin_at = models.DateTimeField(null=True, blank=True)
    checkout_at = models.DateTimeField(null=True, blank=True)

    picked_up_by = EncryptedCharField(max_length=255, blank=True, help_text="Quem buscou (nome)")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Presença ADMSKIDS"
        verbose_name_plural = "Presenças ADMSKIDS"
        ordering = ("-checkin_at",)
        unique_together = ("session", "kid")

    def __str__(self) -> str:
        return f"{self.kid} @ {self.session}"
