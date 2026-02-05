from django.urls import include, path

from .views.auth_views import ForgotPasswordView, LoginView, MeView, ResetPasswordView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth_login"),
    path("auth/me/", MeView.as_view(), name="auth_me"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="auth_forgot_password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="auth_reset_password"),

    # Igreja (CRUD para staff; leitura para autenticados)
    path("church/", include("apps.church.api_urls")),

    # Accounts (admin/staff)
    path("accounts/", include("apps.accounts.api_urls")),

    # ADMSKIDS (CRUD para staff/roles; leitura limitada para responsáveis)
    path("admskids/", include("apps.admskids.api_urls")),

    path("", include("apps.palavra_pastoral.urls")),

    path("aovivo/", include("apps.aovivo.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)