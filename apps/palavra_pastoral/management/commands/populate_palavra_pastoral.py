from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.palavra_pastoral.models import PalavraPastoral


class Command(BaseCommand):
    help = "Popula o banco com registros de PalavraPastoral (idempotente)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Apaga todos os registros de PalavraPastoral antes de popular.",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=8,
            help="Quantidade de itens padrão para gerar (usa a lista base e complementa com extras).",
        )

    def handle(self, *args: Any, **options: Any):
        clear: bool = options["clear"]
        count: int = options["count"]

        if clear:
            deleted, _ = PalavraPastoral.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removidos {deleted} registros."))

        now = timezone.now()

        # Lista base (edite livremente com seus autores reais e URLs reais)
        base_items = [
            {
                "slug": "pp-fe-que-transforma",
                "titulo": "Fé que transforma",
                "tema": "Fé",
                "autor_nome": "Pr. João Silva",
                "autor_cargo": "Pastor",
                "publicado_em": now - timedelta(days=2),
                "descricao": "Uma palavra pastoral sobre perseverança e confiança em Deus.",
                "video_url": "https://www.youtube.com/watch?v=VIDEO_ID_01",
                "plataforma": "youtube",
                "duracao_segundos": 18 * 60,
                "publicado": True,
                "ordem": 0,
                "tags": ["fé", "perseverança"],
            },
            {
                "slug": "pp-oracao-no-secreto",
                "titulo": "Oração no secreto",
                "tema": "Oração",
                "autor_nome": "Pr. Marcos Almeida",
                "autor_cargo": "Pastor",
                "publicado_em": now - timedelta(days=5),
                "descricao": "Como fortalecer sua vida devocional com práticas simples.",
                "video_url": "https://www.youtube.com/watch?v=VIDEO_ID_02",
                "plataforma": "youtube",
                "duracao_segundos": 22 * 60,
                "publicado": True,
                "ordem": 1,
                "tags": ["oração", "devocional"],
            },
            {
                "slug": "pp-familia-proposito",
                "titulo": "Família e propósito",
                "tema": "Família",
                "autor_nome": "Pr. Daniel Souza",
                "autor_cargo": "Pastor",
                "publicado_em": now - timedelta(days=9),
                "descricao": "Princípios para edificar o lar com sabedoria e amor.",
                "video_url": "https://www.facebook.com/watch/?v=VIDEO_ID_03",
                "plataforma": "facebook",
                "duracao_segundos": 26 * 60,
                "publicado": True,
                "ordem": 2,
                "tags": ["família", "relacionamentos"],
            },
            {
                "slug": "pp-santidade-diaria",
                "titulo": "Santidade no dia a dia",
                "tema": "Santidade",
                "autor_nome": "Pr. Paulo Ferreira",
                "autor_cargo": "Pastor",
                "publicado_em": now - timedelta(days=14),
                "descricao": "Aplicando valores do Evangelho em decisões práticas do cotidiano.",
                "video_url": "https://www.youtube.com/watch?v=VIDEO_ID_04",
                "plataforma": "youtube",
                "duracao_segundos": 19 * 60,
                "publicado": True,
                "ordem": 3,
                "tags": ["santidade", "vida cristã"],
            },
        ]

        # Complementa com itens extras se count for maior que a lista base
        items = list(base_items)
        while len(items) < count:
            n = len(items) + 1
            title = f"Mensagem pastoral #{n}"
            items.append(
                {
                    "slug": f"pp-mensagem-{n}",
                    "titulo": title,
                    "tema": "Edificação",
                    "autor_nome": "Pr. Equipe Pastoral",
                    "autor_cargo": "Pastor",
                    "publicado_em": now - timedelta(days=14 + n),
                    "descricao": "Mensagem gerada para preencher dados no ambiente de desenvolvimento.",
                    "video_url": f"https://www.youtube.com/watch?v=VIDEO_ID_{n:02d}",
                    "plataforma": "youtube",
                    "duracao_segundos": (15 + n) * 60,
                    "publicado": True,
                    "ordem": 10 + n,
                    "tags": ["edificação"],
                }
            )

        created = 0
        updated = 0

        tag_model = None
        has_tags_m2m = hasattr(PalavraPastoral, "tags")  # ManyToMany optional
        if has_tags_m2m:
            # Se você criou o model PalavraTag como sugeri antes, ele existe.
            try:
                from apps.palavra_pastoral.models import PalavraTag  # type: ignore
                tag_model = PalavraTag
            except Exception:
                tag_model = None  # existe campo tags mas sem model importável aqui

        for data in items:
            tags = data.pop("tags", [])

            # Segurança: se não informarem slug, cria um estável
            slug = data.get("slug") or slugify(data.get("titulo", ""))[:150] or None
            if not slug:
                continue
            data["slug"] = slug

            obj, was_created = PalavraPastoral.objects.update_or_create(
                slug=slug,
                defaults=data,
            )

            if was_created:
                created += 1
            else:
                updated += 1

            # Tags (opcional)
            if has_tags_m2m and tag_model and tags:
                tag_objs = []
                for t in tags:
                    t = (t or "").strip()
                    if not t:
                        continue
                    tag_obj, _ = tag_model.objects.get_or_create(nome=t)
                    tag_objs.append(tag_obj)
                obj.tags.set(tag_objs)

        self.stdout.write(self.style.SUCCESS(f"Populate concluído: {created} criados, {updated} atualizados."))

