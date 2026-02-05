from django.db import models
from django.utils.text import slugify


class AoVivoCategory(models.Model):
    name = models.CharField("Nome", max_length=80, unique=True)
    slug = models.SlugField("Slug", max_length=90, unique=True, blank=True)
    description = models.TextField("Descrição", blank=True)
    order = models.PositiveIntegerField("Ordem", default=0)
    is_active = models.BooleanField("Ativo", default=True)

    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Categoria (Ao Vivo)"
        verbose_name_plural = "Categorias (Ao Vivo)"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class AoVivoVideo(models.Model):
    class Provider(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        FACEBOOK = "facebook", "Facebook"
        URL = "url", "URL"

    category = models.ForeignKey(
        AoVivoCategory,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="Categoria",
    )

    title = models.CharField("Título", max_length=140)
    subtitle = models.CharField("Subtítulo", max_length=180, blank=True)

    provider = models.CharField(
        "Provedor", max_length=20, choices=Provider.choices, default=Provider.YOUTUBE
    )
    video_url = models.URLField("Link do Vídeo", max_length=500)

    thumbnail_url = models.URLField("Thumbnail (URL)", max_length=500, blank=True)
    published_at = models.DateTimeField("Data de Publicação", null=True, blank=True)

    order = models.PositiveIntegerField("Ordem", default=0)
    is_active = models.BooleanField("Ativo", default=True)

    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Vídeo (Ao Vivo)"
        verbose_name_plural = "Vídeos (Ao Vivo)"
        ordering = ["-published_at", "-created_at", "order"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_active", "provider"]),
        ]

    def __str__(self):
        return f"{self.category.name} - {self.title}"
