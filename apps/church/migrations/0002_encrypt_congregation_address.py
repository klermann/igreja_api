from django.db import migrations

from apps.common.fields import EncryptedCharField


def encrypt_existing_addresses(apps, schema_editor):
    Congregation = apps.get_model("church", "Congregation")

    # Re-saving will encrypt via the model field (EncryptedCharField).
    # The field is backwards compatible, so reading plaintext won't error.
    for obj in Congregation.objects.exclude(address="").iterator():
        obj.address = obj.address  # triggers encryption on save
        obj.save(update_fields=["address"])


class Migration(migrations.Migration):
    dependencies = [
        ("church", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="congregation",
            name="address",
            field=EncryptedCharField(max_length=255, blank=True),
        ),
        migrations.RunPython(encrypt_existing_addresses, migrations.RunPython.noop),
    ]
