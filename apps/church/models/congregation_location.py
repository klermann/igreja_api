# ---------------------------
# JSON: localizacao
# ---------------------------
from django.db import models


class CongregationLocation(models.Model):
    congregation = models.OneToOneField(
        "church.Congregation",
        on_delete=models.CASCADE,
        related_name="location",
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    altitude = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Localização da Congregação"
        verbose_name_plural = "Localizações das Congregações"

    def __str__(self) -> str:
        return f"Localização - {self.congregation.name}"