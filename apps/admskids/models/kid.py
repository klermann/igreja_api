from django.db import models

from apps.common.fields import EncryptedCharField


class Kid(models.Model):
    """Criança cadastrada no ADMSKIDS."""

    class Gender(models.TextChoices):
        MALE = "M", "Masculino"
        FEMALE = "F", "Feminino"
        OTHER = "O", "Outro"

    congregation = models.ForeignKey(
        "church.Congregation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kids",
    )

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)

    # Dados sensíveis (at-rest encryption)
    allergies = EncryptedCharField(max_length=255, blank=True)
    medical_notes = EncryptedCharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    photo = models.ImageField(upload_to="admskids/kids", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Criança"
        verbose_name_plural = "Crianças"
        ordering = ("first_name", "last_name")

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
