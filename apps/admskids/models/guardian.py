from django.conf import settings
from django.db import models

from apps.common.fields import EncryptedCharField


class Guardian(models.Model):
    """Responsável pela criança.

    Pode (opcionalmente) estar vinculado a um User para facilitar o "meus filhos" no app.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kids_guardianships",
    )

    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = EncryptedCharField(max_length=255, blank=True)
    relationship = models.CharField(max_length=50, blank=True, help_text="Ex.: mãe, pai, tio, avó")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Responsável"
        verbose_name_plural = "Responsáveis"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
