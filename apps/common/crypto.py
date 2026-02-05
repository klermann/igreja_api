"""Crypto helpers for at-rest encryption (DB).

This project uses Fernet (symmetric authenticated encryption) from `cryptography`.

Features:
- Key rotation via MultiFernet: decrypt with ANY key, encrypt with the FIRST.
- Backwards compatible: if a value is not marked as encrypted, it's returned as-is.

Important:
- Encrypted values are NOT searchable/sortable by their plaintext.
"""

from __future__ import annotations

from functools import lru_cache

from django.conf import settings

from cryptography.fernet import Fernet, MultiFernet


ENC_PREFIX = "enc$"  # marker to detect encrypted strings


def _get_keyring() -> list[bytes]:
    """Return encryption keys as bytes.

    Configure in .env as a comma-separated list:
      FIELD_ENCRYPTION_KEYS=key1,key2,key3

    - key1 is the primary key used to encrypt new values.
    - older keys remain to decrypt existing values during rotation.
    """

    keys = getattr(settings, "FIELD_ENCRYPTION_KEYS", None) or []
    # django-environ may return list of strings
    return [k.encode() if isinstance(k, str) else k for k in keys]


@lru_cache(maxsize=1)
def get_fernet() -> MultiFernet:
    keyring = _get_keyring()
    if not keyring:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEYS not configured. "
            "Generate a key and set it in your .env (see docs below)."
        )
    fernets = [Fernet(k) for k in keyring]
    return MultiFernet(fernets)


def encrypt_str(value: str) -> str:
    if value is None:
        return value
    if value == "":
        return ""
    if value.startswith(ENC_PREFIX):
        return value
    token = get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")
    return f"{ENC_PREFIX}{token}"


def decrypt_str(value: str) -> str:
    if value is None:
        return value
    if value == "":
        return ""
    if not isinstance(value, str):
        value = str(value)
    if not value.startswith(ENC_PREFIX):
        # plaintext (e.g., existing rows before migration)
        return value
    token = value[len(ENC_PREFIX) :]
    try:
        return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        # If keys are wrong or value corrupted, return raw to avoid hard crashes.
        # Consider logging and/or raising in stricter environments.
        return value
