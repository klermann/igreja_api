from django.db import models


class KidsClass(models.Model):
    """Turma / classe do ministério infantil."""

    congregation = models.ForeignKey(
        "church.Congregation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kids_classes",
    )

    name = models.CharField(max_length=200)
    age_min = models.PositiveIntegerField(null=True, blank=True, help_text="Idade mínima (anos)")
    age_max = models.PositiveIntegerField(null=True, blank=True, help_text="Idade máxima (anos)")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Turma ADMSKIDS"
        verbose_name_plural = "Turmas ADMSKIDS"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
