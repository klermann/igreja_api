from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail


def build_reset_url(raw_token: str) -> str:
    base = (settings.FRONTEND_RESET_URL or "").rstrip("/")
    if base:
        # Frontend can read token from querystring
        return f"{base}?token={raw_token}"

    # Fallback: API endpoint (you can keep this internal)
    return f"/api/auth/reset-password/?token={raw_token}"


def send_password_reset_email(*, to_email: str, raw_token: str) -> None:
    url = build_reset_url(raw_token)
    subject = "Redefinição de senha"
    message = (
        "Você solicitou a redefinição de senha.\n\n"
        f"Abra o link para continuar: {url}\n\n"
        "Se você não solicitou isso, ignore este e-mail."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=True)
