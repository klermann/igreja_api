# ---------------------------
# JSON: detalhes
# ---------------------------
from django.db import models


class CongregationDetails(models.Model):
    congregation = models.OneToOneField(
        "church.Congregation",
        on_delete=models.CASCADE,
        related_name="details",
    )
    tipo_local = models.CharField(max_length=120, blank=True)
    descricao = models.TextField(blank=True)
    ponto_referencia = models.CharField(max_length=255, blank=True)
    horario_funcionamento = models.CharField(max_length=255, blank=True)
    acessibilidade = models.CharField(max_length=255, blank=True)
    estacionamento = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Detalhes da Congregação"
        verbose_name_plural = "Detalhes das Congregações"

    def __str__(self) -> str:
        return f"Detalhes - {self.congregation.name}"
