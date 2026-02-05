from django.db import models
from django.utils.text import slugify
from django.utils import timezone

class PalavraPastoral(models.Model):
    PLATFORM_CHOICES = [
        ("youtube", "YouTube"),
        ("facebook", "Facebook"),
        ("vimeo", "Vimeo"),
        ("mp4", "MP4 (direto)"),
        ("other", "Outro"),
    ]

    # Conteúdo principal
    titulo = models.CharField(max_length=140)
    autor_nome = models.CharField(max_length=120)
    autor_cargo = models.CharField(max_length=80, blank=True)  # ex: Pastor, Presbítero, etc.
    publicado_em = models.DateTimeField(default=timezone.now)

    descricao = models.TextField(blank=True)
    tema = models.CharField(max_length=120, blank=True)  # opcional (ex: “Atitudes Transformadoras”)

    # Vídeo
    video_url = models.URLField()
    plataforma = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="youtube")
    duracao_segundos = models.PositiveIntegerField(default=0)

    # Imagens (thumb para lista + capa opcional)
    thumbnail = models.ImageField(upload_to="palavra_pastoral/thumbs/", blank=True, null=True)
    capa = models.ImageField(upload_to="palavra_pastoral/capas/", blank=True, null=True)

    # Publicação/ordenação
    publicado = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=170, unique=True, blank=True)

    # Métricas simples (p/ futuro)
    views_count = models.PositiveIntegerField(default=0, editable=False)
    shares_count = models.PositiveIntegerField(default=0, editable=False)

    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publicado_em", "ordem", "-id"]
        verbose_name = "Palavra Pastoral"
        verbose_name_plural = "Palavras Pastorais"

    def __str__(self):
        return f"{self.titulo} — {self.autor_nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)[:140] or "palavra-pastoral"
            candidate = base
            i = 2
            while PalavraPastoral.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)
