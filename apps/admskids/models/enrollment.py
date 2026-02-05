from django.db import models


class Enrollment(models.Model):
    """Matrícula de criança em uma turma."""

    kid = models.ForeignKey("admskids.Kid", on_delete=models.CASCADE, related_name="enrollments")
    kids_class = models.ForeignKey("admskids.KidsClass", on_delete=models.CASCADE, related_name="enrollments")

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Matrícula ADMSKIDS"
        verbose_name_plural = "Matrículas ADMSKIDS"
        ordering = ("-start_date",)
        constraints = [
            models.UniqueConstraint(fields=["kid", "kids_class"], name="uniq_kid_class_enrollment")
        ]

    def __str__(self) -> str:
        return f"{self.kid} → {self.kids_class}"
