from django.db import models


# ---------------------------
# JSON: imagens
# ---------------------------
class CongregationImages(models.Model):
    congregation = models.OneToOneField(
        "church.Congregation",
        on_delete=models.CASCADE,
        related_name="images",
    )
    imagem_estatica = models.URLField(blank=True)
    imagem_streetview = models.URLField(blank=True)
    thumbnail = models.URLField(blank=True)

    # lista de URLs
    galeria_imagens = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = "Imagens da Congregação"
        verbose_name_plural = "Imagens das Congregações"

    def __str__(self) -> str:
        return f"Imagens - {self.congregation.name}"

