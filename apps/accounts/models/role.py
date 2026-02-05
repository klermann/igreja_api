from django.db import models


class Role(models.Model):
    """Role-based access control.

    Keep roles in DB so you can add new roles without changing code.
    The API can still expose roles as simple strings (role.code).
    """

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    priority = models.PositiveIntegerField(default=100, help_text="Lower = higher priority")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Perfi"
        ordering = ("priority", "code")

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"
