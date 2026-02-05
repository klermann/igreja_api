# apps/api/management/commands/populate_db.py
from __future__ import annotations

import random
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models import Role, User
from apps.church.models import Church, Congregation
from apps.admskids.models import (
    Kid,
    Guardian,
    KidGuardian,
    KidsClass,
    Enrollment,
    ClassSession,
    KidAttendance,
)


def _pick(seq):
    return random.choice(list(seq))


def _unique_slug(model, base_slug: str, *, scope: dict | None = None, field: str = "slug") -> str:
    """Generate a unique slug optionally within a scope (filter)."""
    scope = scope or {}
    base_slug = (base_slug or "item")[:200]
    slug = base_slug
    i = 2
    while model.objects.filter(**scope, **{field: slug}).exists():
        slug = f"{base_slug}-{i}"[:200]
        i += 1
    return slug


def _ct_perms_for_models(app_label: str, model_names: list[str]) -> list[Permission]:
    """Return Django default perms for model list: add/change/delete/view."""
    perms: list[Permission] = []
    for m in model_names:
        ct = ContentType.objects.get(app_label=app_label, model=m)
        perms += list(Permission.objects.filter(content_type=ct))
    return perms


class Command(BaseCommand):
    help = "Popula o banco com dados completos (accounts, church, admskids) + grupos/permissões."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=42, help="Seed random (default: 42)")
        parser.add_argument("--password", default="Senha@123", help="Senha padrão (default: Senha@123)")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Limpa e recria apenas dados de CHURCH/ADMSKIDS (não remove users/roles), útil para re-popular.",
        )
        parser.add_argument(
            "--wipe-all",
            action="store_true",
            help="Apaga TUDO que é do projeto (accounts/church/admskids) e recria do zero. (Cuidado!)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(options["seed"])
        password = options["password"]
        force = options["force"]
        wipe_all = options["wipe_all"]

        # ---------------------------------------------------------------------
        # HARD REQUIREMENT: encryption keys
        # ---------------------------------------------------------------------
        # Mesmo com DEBUG=True, salvar campos EncryptedCharField exige chaves.
        if not getattr(settings, "FIELD_ENCRYPTION_KEYS", None):
            raise CommandError(
                "FIELD_ENCRYPTION_KEYS não configurado.\n"
                "Gere uma chave Fernet e defina no seu .env:\n"
                "  python -c \"import os,base64; print(base64.urlsafe_b64encode(os.urandom(32)).decode())\"\n"
                "  FIELD_ENCRYPTION_KEYS=sua_chave_aqui\n"
            )

        self.stdout.write(self.style.MIGRATE_HEADING("== Populate DB =="))

        # ---------------------------------------------------------------------
        # Optional cleanup
        # ---------------------------------------------------------------------
        if wipe_all:
            self.stdout.write(self.style.WARNING("[wipe-all] Apagando dados do projeto..."))
            # admskids
            KidAttendance.objects.all().delete()
            ClassSession.objects.all().delete()
            Enrollment.objects.all().delete()
            KidGuardian.objects.all().delete()
            Kid.objects.all().delete()
            Guardian.objects.all().delete()
            KidsClass.objects.all().delete()
            # church
            Congregation.objects.all().delete()
            Church.objects.all().delete()
            # accounts
            # NOTE: mantém superuser do django? aqui vamos remover Users também.
            User.objects.all().delete()
            Role.objects.all().delete()
            Group.objects.all().delete()

        elif force:
            self.stdout.write(self.style.WARNING("[force] Limpando CHURCH/ADMSKIDS (mantém users/roles)..."))
            KidAttendance.objects.all().delete()
            ClassSession.objects.all().delete()
            Enrollment.objects.all().delete()
            KidGuardian.objects.all().delete()
            Kid.objects.all().delete()
            Guardian.objects.all().delete()
            KidsClass.objects.all().delete()
            Congregation.objects.all().delete()
            Church.objects.all().delete()

        # ---------------------------------------------------------------------
        # 1) Roles (RBAC)
        # ---------------------------------------------------------------------
        roles = self._ensure_roles()
        self.stdout.write(self.style.SUCCESS(f"Roles OK: {', '.join(roles.keys())}"))

        # ---------------------------------------------------------------------
        # 2) Churches + Congregations
        # ---------------------------------------------------------------------
        churches = self._ensure_churches()
        self.stdout.write(self.style.SUCCESS(f"Igrejas OK: {len(churches)}"))

        congregations = self._ensure_congregations(churches)
        self.stdout.write(self.style.SUCCESS(f"Congregações OK: {len(congregations)}"))

        # ---------------------------------------------------------------------
        # 3) Users (admin/pastores/lideres/professores/guardians como users)
        # ---------------------------------------------------------------------
        admin_user = self._ensure_admin(password=password, roles=roles, congregations=congregations)
        pastors = self._ensure_staff_users(
            base_email="pastor",
            count=2,
            password=password,
            role=roles["pastor"],
            extra_role=roles["admskids_admin"],
            congregations=congregations,
            staff=True,
        )
        leaders = self._ensure_staff_users(
            base_email="leader",
            count=2,
            password=password,
            role=roles["leader"],
            extra_role=None,
            congregations=congregations,
            staff=True,
        )
        teachers = self._ensure_staff_users(
            base_email="professor",
            count=5,
            password=password,
            role=roles["professor"],
            extra_role=roles["admskids_worker"],
            congregations=congregations,
            staff=True,
        )

        # ---------------------------------------------------------------------
        # 4) Django Groups + Permissions (opcional, mas útil no admin)
        # ---------------------------------------------------------------------
        self._ensure_groups_and_perms()

        # ---------------------------------------------------------------------
        # 5) ADMSKIDS: guardians, kids, links, classes, enrollments, sessions, attendances
        # ---------------------------------------------------------------------
        guardian_users = self._ensure_guardian_users(
            count=10,
            password=password,
            role=roles["guardian"],
            congregations=congregations,
        )
        guardians = self._ensure_guardians(guardian_users)

        kids = self._ensure_kids(count=20, congregations=congregations)
        self._ensure_kid_guardian_links(kids, guardians)

        classes = self._ensure_classes(congregations)
        enrollments = self._ensure_enrollments(kids, classes)

        sessions = self._ensure_sessions(classes, teachers)
        self._ensure_attendances(sessions, enrollments, guardians)

        self.stdout.write(self.style.SUCCESS("Populate concluído com sucesso!"))
        self.stdout.write("\nAcessos padrão:")
        self.stdout.write(f"- admin: admin@igreja.local / {password}")
        self.stdout.write(f"- professores: professor1@igreja.local ... professor5@igreja.local / {password}")
        self.stdout.write(f"- guardians users: guardian1@igreja.local ... guardian10@igreja.local / {password}")

    # -------------------------------------------------------------------------
    # Builders
    # -------------------------------------------------------------------------

    def _ensure_roles(self) -> dict[str, Role]:
        role_defs = [
            ("admin", "Administrador", 1),
            ("pastor", "Pastor", 10),
            ("leader", "Líder", 20),
            ("professor", "Professor", 30),
            ("admskids_admin", "ADMSKIDS Admin", 40),
            ("admskids_worker", "ADMSKIDS Worker", 50),
            ("guardian", "Responsável", 60),
        ]
        out: dict[str, Role] = {}
        for code, name, prio in role_defs:
            role, _ = Role.objects.get_or_create(
                code=code,
                defaults={"name": name, "priority": prio, "is_active": True},
            )
            changed = False
            if role.name != name:
                role.name = name
                changed = True
            if role.priority != prio:
                role.priority = prio
                changed = True
            if not role.is_active:
                role.is_active = True
                changed = True
            if changed:
                role.save(update_fields=["name", "priority", "is_active"])
            out[code] = role
        return out

    def _ensure_churches(self) -> list[Church]:
        churches_data = [
            ("Igreja Sede Central", "São Paulo", "SP"),
            ("Igreja Vida Nova", "Campinas", "SP"),
            ("Igreja Esperança", "Sorocaba", "SP"),
            ("Igreja Cristo Vive", "Santos", "SP"),
            ("Igreja Avivamento", "Ribeirão Preto", "SP"),
        ]
        churches: list[Church] = []
        for name, city, state in churches_data:
            base_slug = slugify(name)
            slug = _unique_slug(Church, base_slug)
            obj, created = Church.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "city": city, "state": state, "is_active": True},
            )
            if not created:
                changed = False
                for f, v in (("name", name), ("city", city), ("state", state)):
                    if getattr(obj, f) != v:
                        setattr(obj, f, v)
                        changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save()
            churches.append(obj)
        return churches

    def _ensure_congregations(self, churches: list[Church]) -> list[Congregation]:
        cong_data = [
            ("Congregação Centro", "São Paulo", "SP"),
            ("Congregação Zona Sul", "São Paulo", "SP"),
            ("Congregação Zona Norte", "São Paulo", "SP"),
            ("Congregação Campinas 1", "Campinas", "SP"),
            ("Congregação Campinas 2", "Campinas", "SP"),
            ("Congregação Sorocaba", "Sorocaba", "SP"),
            ("Congregação Santos", "Santos", "SP"),
            ("Congregação Ribeirão", "Ribeirão Preto", "SP"),
            ("Congregação Interior", "Jundiaí", "SP"),
            ("Congregação Litoral", "Guarujá", "SP"),
        ]
        congregations: list[Congregation] = []
        for i, (name, city, state) in enumerate(cong_data, start=1):
            church = churches[(i - 1) % len(churches)]
            base_slug = slugify(name)
            slug = _unique_slug(Congregation, base_slug, scope={"church": church})
            obj, created = Congregation.objects.get_or_create(
                church=church,
                slug=slug,
                defaults={
                    "name": name,
                    "city": city,
                    "state": state,
                    "address": f"Rua {i}, {100+i} - {city}",
                    "is_active": True,
                },
            )
            if not created:
                changed = False
                for f, v in (("name", name), ("city", city), ("state", state)):
                    if getattr(obj, f) != v:
                        setattr(obj, f, v)
                        changed = True
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if changed:
                    obj.save()
            congregations.append(obj)
        return congregations

    def _ensure_admin(self, *, password: str, roles: dict[str, Role], congregations: list[Congregation]) -> User:
        email = "admin@igreja.local"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": "Administrador Geral",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
                "congregation": _pick(congregations),
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])
        else:
            dirty = False
            if not user.is_staff:
                user.is_staff = True
                dirty = True
            if not user.is_superuser:
                user.is_superuser = True
                dirty = True
            if not user.is_active:
                user.is_active = True
                dirty = True
            if not user.congregation:
                user.congregation = _pick(congregations)
                dirty = True
            if dirty:
                user.save()

        user.roles.add(roles["admin"], roles["admskids_admin"])
        return user

    def _ensure_staff_users(
        self,
        *,
        base_email: str,
        count: int,
        password: str,
        role: Role,
        extra_role: Role | None,
        congregations: list[Congregation],
        staff: bool = True,
    ) -> list[User]:
        first_names = ["Ana", "Bruno", "Carla", "Diego", "Elisa", "Felipe", "Gi", "Henrique", "Isabela", "João"]
        last_names = ["Silva", "Souza", "Oliveira", "Santos", "Lima", "Pereira", "Costa", "Ferreira", "Alves", "Gomes"]

        users: list[User] = []
        for i in range(1, count + 1):
            email = f"{base_email}{i}@igreja.local"
            name = f"{_pick(first_names)} {_pick(last_names)}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "is_staff": staff,
                    "is_active": True,
                    "congregation": congregations[(i - 1) % len(congregations)],
                },
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            else:
                dirty = False
                if staff and not user.is_staff:
                    user.is_staff = True
                    dirty = True
                if not user.is_active:
                    user.is_active = True
                    dirty = True
                if not user.congregation:
                    user.congregation = congregations[(i - 1) % len(congregations)]
                    dirty = True
                if dirty:
                    user.save()

            user.roles.add(role)
            if extra_role:
                user.roles.add(extra_role)
            users.append(user)

        return users

    def _ensure_groups_and_perms(self):
        """
        Cria grupos do Django com permissões padrão (add/change/delete/view) por app/model.
        Isso ajuda muito quando você quer controlar o acesso pelo admin usando Groups.
        """
        # Mapeia "grupo" -> permissões por models
        groups_def = {
            "ADMSKIDS Admin": _ct_perms_for_models("admskids", ["kid", "guardian", "kidguardian", "kidsclass", "enrollment", "classsession", "kidattendance"])
            + _ct_perms_for_models("church", ["church", "congregation"]),
            "ADMSKIDS Worker": _ct_perms_for_models("admskids", ["kid", "guardian", "kidguardian", "kidsclass", "enrollment", "classsession", "kidattendance"]),
            "Professores": _ct_perms_for_models("admskids", ["classsession", "kidattendance"]) + _ct_perms_for_models("admskids", ["kid", "enrollment", "kidsclass"]),
            "Igreja Admin": _ct_perms_for_models("church", ["church", "congregation"]),
        }

        for gname, perms in groups_def.items():
            g, _ = Group.objects.get_or_create(name=gname)
            if perms:
                g.permissions.set(perms)

    def _ensure_guardian_users(self, *, count: int, password: str, role: Role, congregations: list[Congregation]) -> list[User]:
        """
        Cria usuários para responsáveis (útil pro app "Meus filhos").
        """
        users: list[User] = []
        for i in range(1, count + 1):
            email = f"guardian{i}@igreja.local"
            name = f"Responsável {i}"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "name": name,
                    "is_staff": False,
                    "is_active": True,
                    "congregation": _pick(congregations),
                },
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])
            user.roles.add(role)
            users.append(user)
        return users

    def _ensure_guardians(self, guardian_users: list[User]) -> list[Guardian]:
        relationships = ["mãe", "pai", "avó", "tio", "tia"]
        guardians: list[Guardian] = []

        for idx, u in enumerate(guardian_users, start=1):
            # evita duplicação: 1 Guardian por user
            obj, created = Guardian.objects.get_or_create(
                user=u,
                defaults={
                    "name": u.name,
                    "email": u.email,
                    "phone": f"+55 11 9{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                    "relationship": _pick(relationships),
                    "is_active": True,
                },
            )
            if not created:
                changed = False
                if not obj.is_active:
                    obj.is_active = True
                    changed = True
                if not obj.email:
                    obj.email = u.email
                    changed = True
                if changed:
                    obj.save()
            guardians.append(obj)

        return guardians

    def _ensure_kids(self, *, count: int, congregations: list[Congregation]) -> list[Kid]:
        first = [
            "Ana", "Bia", "Caio", "Davi", "Ester", "Fábio", "Gabi", "Heitor", "Iara", "Joana",
            "Kauan", "Lara", "Miguel", "Nina", "Otávio", "Pietra", "Ravi", "Sofia", "Theo", "Valentina"
        ]
        last = ["Silva", "Souza", "Oliveira", "Santos", "Lima", "Pereira", "Costa", "Ferreira", "Alves", "Gomes"]
        allergies_samples = ["", "Lactose", "Glúten", "Amendoim", "Ovos"]
        medical_samples = ["", "Asma (leve)", "Rinite", "Alergia sazonal", ""]

        kids: list[Kid] = []
        for i in range(1, count + 1):
            fn = first[(i - 1) % len(first)]
            ln = _pick(last)
            birth = date.today() - timedelta(days=random.randint(3 * 365, 12 * 365))
            gender = _pick([Kid.Gender.MALE, Kid.Gender.FEMALE, Kid.Gender.OTHER])
            cong = _pick(congregations)

            # Garantir idempotência: usa (first_name, last_name, congregation) como chave "prática"
            obj, created = Kid.objects.get_or_create(
                first_name=fn,
                last_name=ln,
                congregation=cong,
                defaults={
                    "birth_date": birth,
                    "gender": gender,
                    "allergies": _pick(allergies_samples),
                    "medical_notes": _pick(medical_samples),
                    "notes": "" if random.random() < 0.6 else "Observação de exemplo",
                    "is_active": True,
                },
            )
            if not created and not obj.is_active:
                obj.is_active = True
                obj.save(update_fields=["is_active"])

            kids.append(obj)

        return kids

    def _ensure_kid_guardian_links(self, kids: list[Kid], guardians: list[Guardian]):
        for kid in kids:
            g1 = _pick(guardians)
            g2 = _pick([g for g in guardians if g != g1]) if len(guardians) > 1 else g1

            KidGuardian.objects.get_or_create(kid=kid, guardian=g1, defaults={"is_primary": True})
            if random.random() < 0.7:
                KidGuardian.objects.get_or_create(kid=kid, guardian=g2, defaults={"is_primary": False})

    def _ensure_classes(self, congregations: list[Congregation]) -> list[KidsClass]:
        base_classes = [
            ("Berçário", 0, 2),
            ("Infantil 1", 3, 5),
            ("Infantil 2", 6, 8),
        ]
        classes: list[KidsClass] = []
        for cong in congregations:
            for cname, amin, amax in base_classes:
                name = f"{cname} - {cong.name}"
                obj, _ = KidsClass.objects.get_or_create(
                    congregation=cong,
                    name=name,
                    defaults={"age_min": amin, "age_max": amax, "is_active": True},
                )
                classes.append(obj)
        return classes

    def _ensure_enrollments(self, kids: list[Kid], classes: list[KidsClass]) -> list[Enrollment]:
        enrollments: list[Enrollment] = []
        for kid in kids:
            possible = [c for c in classes if c.congregation_id == kid.congregation_id] or classes
            kids_class = _pick(possible)
            obj, _ = Enrollment.objects.get_or_create(
                kid=kid,
                kids_class=kids_class,
                defaults={"is_active": True},
            )
            enrollments.append(obj)
        return enrollments

    def _ensure_sessions(self, classes: list[KidsClass], teachers: list[User]) -> list[ClassSession]:
        """
        Cria 4 sessões (últimos 4 domingos) para cada turma.
        """
        today = timezone.localdate()
        days_since_sun = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sun)
        session_dates = [last_sunday - timedelta(weeks=w) for w in range(0, 4)]

        sessions: list[ClassSession] = []
        for idx, kids_class in enumerate(classes):
            created_by = teachers[idx % len(teachers)] if teachers else None
            for d in session_dates:
                obj, _ = ClassSession.objects.get_or_create(
                    kids_class=kids_class,
                    date=d,
                    defaults={"created_by": created_by, "notes": "Sessão gerada automaticamente"},
                )
                sessions.append(obj)
        return sessions

    def _ensure_attendances(self, sessions: list[ClassSession], enrollments: list[Enrollment], guardians: list[Guardian]):
        """
        Para cada sessão, marca presença para todas as crianças matriculadas naquela turma.
        """
        now = timezone.now()
        enroll_by_class: dict[int, list[Enrollment]] = {}
        for enr in enrollments:
            enroll_by_class.setdefault(enr.kids_class_id, []).append(enr)

        for sess in sessions:
            enrs = enroll_by_class.get(sess.kids_class_id, [])
            for enr in enrs:
                kid = enr.kid
                present = random.random() < 0.8
                status = KidAttendance.Status.PRESENT if present else KidAttendance.Status.ABSENT

                # horários simulados
                checkin = None
                checkout = None
                picked_up_by = ""
                if present:
                    checkin = now - timedelta(hours=random.randint(1, 72))
                    checkout = checkin + timedelta(hours=1, minutes=random.randint(10, 50))
                    picked_up_by = _pick(guardians).name if guardians else "Responsável"

                KidAttendance.objects.get_or_create(
                    session=sess,
                    kid=kid,
                    defaults={
                        "status": status,
                        "checkin_at": checkin,
                        "checkout_at": checkout,
                        "picked_up_by": picked_up_by,
                        "notes": "" if present else "Faltou",
                    },
                )
