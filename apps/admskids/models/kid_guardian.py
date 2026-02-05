from django.db import models


class KidGuardian(models.Model):
    """Relacionamento N:N entre criança e responsável."""

    kid = models.ForeignKey("admskids.Kid", on_delete=models.CASCADE, related_name="kid_guardians")
    guardian = models.ForeignKey("admskids.Guardian", on_delete=models.CASCADE, related_name="guardian_kids")
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Vínculo Criança-Responsável"
        verbose_name_plural = "Vínculos Criança-Responsável"
        unique_together = ("kid", "guardian")

    def __str__(self) -> str:
        return f"{self.kid} ↔ {self.guardian}"
