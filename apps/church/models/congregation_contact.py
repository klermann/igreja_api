from django.db import models

from apps.common.fields import EncryptedCharField


# ---------------------------
# JSON: contato
# ---------------------------
class CongregationContact(models.Model):
    congregation = models.OneToOneField(
        "church.Congregation",
        on_delete=models.CASCADE,
        related_name="contact",
    )
    telefone = EncryptedCharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    # pode guardar {"facebook": "...", "instagram": "..."} etc.
    redes_sociais = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Contato da Congregação"
        verbose_name_plural = "Contatos das Congregações"

    def __str__(self) -> str:
        return f"Contato - {self.congregation.name}"
