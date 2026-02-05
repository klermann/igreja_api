from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone

from apps.aovivo.models import AoVivoCategory, AoVivoVideo


DEFAULT_CATEGORIES = [
    ("CULTO DE ENSINO", 10),
    ("CULTO DA FAMÍLIA", 20),
    ("QUINTA PROFÉTICA", 30),
    ("SANTA CEIA", 40),
    ("CONGRESSOS", 50),
    ("DIA COM DEUS", 60),
]


class Command(BaseCommand):
    help = "Cria categorias padrão do Ao Vivo e gera vídeos (opcional)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--with-sample-videos",
            action="store_true",
            help="Cria vídeos de exemplo (padrão: 1 por categoria se --count não for informado).",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=0,
            help="Quantidade de vídeos de exemplo POR CATEGORIA (ex.: --count 30).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        created_cats = 0
        updated_cats = 0

        for name, order in DEFAULT_CATEGORIES:
            slug = slugify(name)
            obj, created = AoVivoCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "order": order,
                    "is_active": True,
                },
            )

            if created:
                created_cats += 1
            else:
                changed = False
                if obj.name != name:
                    obj.name = name
                    changed = True
                if obj.order != order:
                    obj.order = order
                    changed = True
                if obj.is_active is False:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save(update_fields=["name", "order", "is_active", "updated_at"])
                    updated_cats += 1

        self.stdout.write(self.style.SUCCESS(
            f"Categorias OK. Criadas: {created_cats} | Atualizadas: {updated_cats}"
        ))

        count = int(options["count"] or 0)
        if options["with_sample_videos"] or count > 0:
            self._create_sample_videos(count=count)
            self.stdout.write(self.style.SUCCESS("Vídeos de exemplo criados/ajustados."))

    def _create_sample_videos(self, count: int = 0):
        """
        Cria vídeos idempotentes.
        - Se count=0 -> cria 1 por categoria.
        - Se count>0 -> cria count por categoria.
        """
        now = timezone.now()
        per_category = count if count > 0 else 1

        for cat in AoVivoCategory.objects.all().order_by("order", "name"):
            for i in range(1, per_category + 1):
                title = f"{cat.name} - {i:02d}"
                AoVivoVideo.objects.get_or_create(
                    category=cat,
                    title=title,
                    defaults={
                        "subtitle": "Assembleia de Deus - Ministério de ...",
                        "provider": AoVivoVideo.Provider.YOUTUBE,
                        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                        "thumbnail_url": "",
                        "published_at": now,
                        "order": i,
                        "is_active": True,
                    },
                )
