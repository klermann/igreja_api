from __future__ import annotations

from django.db import models

from .crypto import decrypt_str, encrypt_str


class EncryptedCharField(models.CharField):
    """CharField that encrypts values before saving to DB and decrypts on read.

    - Stores encrypted text prefixed with `enc$...`.
    - Backwards compatible: if the stored value is plaintext, returns plaintext.
    """

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return encrypt_str(str(value))

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt_str(value)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, str):
            return decrypt_str(value)
        return value
