from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role, User
from apps.church.models import Church, Congregation


class Command(BaseCommand):
    help = "Create initial roles, a church, a congregation and an admin user."

    def add_arguments(self, parser):
        parser.add_argument("--admin-email", default="admin@igreja.com")
        parser.add_argument("--admin-password", default="admin123")

    @transaction.atomic
    def handle(self, *args, **opts):
        roles_data = [
            ("admin", "Admin", 10),
            ("pastor", "Pastor", 20),
            ("leader", "Líder", 30),
            ("member", "Membro", 40),
        ]

        roles = {}
        for code, name, priority in roles_data:
            role, _ = Role.objects.update_or_create(
                code=code,
                defaults={"name": name, "priority": priority, "is_active": True},
            )
            roles[code] = role

        church, _ = Church.objects.update_or_create(
            slug="sede",
            defaults={"name": "Igreja Sede", "city": "", "state": ""},
        )
        congregation, _ = Congregation.objects.update_or_create(
            church=church,
            slug="centro",
            defaults={"name": "Sede - Centro", "city": "", "state": ""},
        )

        admin_email = opts["admin_email"].strip().lower()
        admin_password = opts["admin_password"]

        user, created = User.objects.get_or_create(
            email=admin_email,
            defaults={"name": "Administrador", "is_staff": True, "is_superuser": True, "is_active": True},
        )
        if created:
            user.set_password(admin_password)
            user.congregation = congregation
            user.save()

        user.roles.add(roles["admin"])

        self.stdout.write(self.style.SUCCESS("Seed concluído."))
        self.stdout.write(f"Admin: {admin_email} / {admin_password}")
