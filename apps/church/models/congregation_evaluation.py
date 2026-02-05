from django.db import models


# ---------------------------
# JSON: avaliacao
# ---------------------------
class CongregationEvaluation(models.Model):
    congregation = models.OneToOneField(
        "church.Congregation",
        on_delete=models.CASCADE,
        related_name="evaluation",
    )
    nota_media = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    numero_avaliacoes = models.PositiveIntegerField(default=0)

    # lista de strings
    comentarios = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Avaliação da Congregação"
        verbose_name_plural = "Avaliações das Congregações"

    def __str__(self) -> str:
        return f"Avaliação - {self.congregation.name}"
