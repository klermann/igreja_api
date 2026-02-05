from django.conf import settings
from django.db import models


class ClassSession(models.Model):
    """Um encontro/aula/culto infantil para uma turma em uma data."""

    kids_class = models.ForeignKey("admskids.KidsClass", on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_kids_sessions",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sessão ADMSKIDS"
        verbose_name_plural = "Sessões ADMSKIDS"
        ordering = ("-date", "-created_at")
        constraints = [
            models.UniqueConstraint(fields=["kids_class", "date"], name="uniq_class_date_session")
        ]

    def __str__(self) -> str:
        return f"{self.kids_class} - {self.date}"
