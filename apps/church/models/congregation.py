from django.db import models
from apps.common.fields import EncryptedCharField

class Congregation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ativo", "Ativo"
        INACTIVE = "inativo", "Inativo"

    church = models.ForeignKey(
        "church.Church",
        verbose_name="Igreja",
        on_delete=models.CASCADE,
        related_name="congregations",
    )

    # JSON: nome
    name = models.CharField(max_length=200)

    slug = models.SlugField(max_length=200)

    # JSON: cidade
    city = models.CharField(max_length=120, blank=True)

    state = models.CharField(max_length=2, blank=True)

    # JSON: endereco (sensível)
    address = EncryptedCharField(max_length=255, blank=True)

    # JSON: cep
    cep = models.CharField(max_length=20, blank=True)

    # JSON: status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    # compatibilidade com lógica antiga
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Congregação"
        verbose_name_plural = "Congregações"
        unique_together = ("church", "slug")
        ordering = ("church__name", "name")

    def save(self, *args, **kwargs):
        # mantém consistência: status <-> is_active
        self.is_active = (self.status == self.Status.ACTIVE)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} - {self.church.name}"
