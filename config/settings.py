from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------------
# ENV
# ----------------------------------------------------------------------------
# Create a .env based on .env.example
env = environ.Env(
    # Secure defaults: production should be safe even if .env is missing.
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    CORS_ALLOWED_ORIGINS=(list, []),
    SECRET_KEY=(str, ""),
    # Comma-separated Fernet keys, first is primary. Example:
    # FIELD_ENCRYPTION_KEYS=key1,key2
    FIELD_ENCRYPTION_KEYS=(list, []),
    DB_ENGINE=(str, "sqlite"),  # sqlite | mysql
    DB_NAME=(str, str(BASE_DIR / "db.sqlite3")),
    DB_USER=(str, ""),
    DB_PASSWORD=(str, ""),
    DB_HOST=(str, ""),
    DB_PORT=(str, ""),

    # Email (password reset)
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    DEFAULT_FROM_EMAIL=(str, "no-reply@localhost"),
    EMAIL_HOST=(str, ""),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ""),
    EMAIL_HOST_PASSWORD=(str, ""),
    EMAIL_USE_TLS=(bool, True),
    # Optional: frontend URL used to build reset link
    FRONTEND_RESET_URL=(str, ""),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY in {"change-me", "changeme"}:
    raise RuntimeError("SECRET_KEY inválida. Configure uma SECRET_KEY forte no .env")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# Auth (frontend backoffice)
LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/painel/"

# Field-level encryption keys (Fernet). First key is used to encrypt new data.
FIELD_ENCRYPTION_KEYS = env("FIELD_ENCRYPTION_KEYS")
if not DEBUG and not FIELD_ENCRYPTION_KEYS:
    raise RuntimeError("FIELD_ENCRYPTION_KEYS não configurado. Gere uma chave Fernet e defina no .env")

# ----------------------------------------------------------------------------
# APPS
# ----------------------------------------------------------------------------
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",

    # Local
    "apps.accounts",
    "apps.church",
    "apps.admskids",
    "apps.frontend",
    "apps.api",
    "apps.palavra_pastoral",
    "apps.aovivo.apps.AoVivoConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.locale.LocaleMiddleware",

    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# ----------------------------------------------------------------------------
# DATABASE
# ----------------------------------------------------------------------------
DB_ENGINE = env("DB_ENGINE")

if DB_ENGINE == "mysql":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT") or "3306",
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": env("DB_NAME"),
        }
    }

# ----------------------------------------------------------------------------
# AUTH
# ----------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------------------------------------------------------
# I18N
# ----------------------------------------------------------------------------
LANGUAGE_CODE = "pt-br"

USE_I18N = True
USE_L10N = True  # (Django 4.2 ainda aceita; pode manter)
USE_TZ = True

TIME_ZONE = "America/Sao_Paulo"

# Formatos pt-br (deixa datas/números como pt-BR no admin)
DATE_FORMAT = "d/m/Y"
DATETIME_FORMAT = "d/m/Y H:i"
TIME_FORMAT = "H:i"
SHORT_DATE_FORMAT = "d/m/Y"
SHORT_DATETIME_FORMAT = "d/m/Y H:i"

# Se você quer fixar idioma SEM depender do navegador:
LANGUAGES = [
    ("pt-br", "Português (Brasil)"),
]

# ----------------------------------------------------------------------------
# STATIC/MEDIA
# ----------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------------------------------------------------------
# EMAIL (password reset)
# ----------------------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")

FRONTEND_RESET_URL = env("FRONTEND_RESET_URL")

# ----------------------------------------------------------------------------
# DRF
# ----------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Rate limiting (anti brute-force / abuso)
REST_FRAMEWORK.update(
    {
        "DEFAULT_THROTTLE_CLASSES": (
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ),
        "DEFAULT_THROTTLE_RATES": {
            "anon": "30/min",
            "user": "120/min",
            "login": "5/min",
            "forgot": "5/min",
            "reset": "5/min",
        },
    }
)

if not DEBUG:
    # In production, return JSON only (avoid exposing the Browsable API)
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
        "rest_framework.renderers.JSONRenderer",
    )

SPECTACULAR_SETTINGS = {
    "TITLE": "AD Santos - SP",
    "DESCRIPTION": "API AD Santos - SP (roles, congregações, autenticação JWT).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Explicit tag list to keep Swagger UI grouped and ordered.
    "TAGS": [
        {"name": "Auth", "description": "Autenticação JWT, /me e reset de senha"},
        {"name": "Palavra pastoral", "description": "Módulo Palavra Pastoral: Palavra Pastoral"},
        {"name": "Igreja", "description": "Cadastro de Igreja e Congregações"},
        {"name": "ADMSKIDS", "description": "Módulo ADMSKIDS: crianças, responsáveis, turmas e presenças"},
    ],
}

# ----------------------------------------------------------------------------
# UNFOLD (Admin Theme)
# ----------------------------------------------------------------------------
# Docs: https://unfoldadmin.com/  |  PyPI: django-unfold
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_TITLE": "Igreja API",
    "SITE_HEADER": "Igreja API • Administração",
    "SITE_URL": "/",
    "SITE_SYMBOL": "church",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "LOGIN": {
        "image": lambda request: static("frontend/img/login-bg.svg"),
    },
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "navigation": [
            {
                "title": _("Acesso"),
                "items": [
                    {"title": _("Usuários"), "icon": "person", "link": reverse_lazy("admin:accounts_user_changelist")},
                    {"title": _("Roles"), "icon": "verified_user",
                     "link": reverse_lazy("admin:accounts_role_changelist")},
                    {"title": _("Grupos"), "icon": "group", "link": reverse_lazy("admin:auth_group_changelist")},
                ],
            },
            {
                "title": _("Igreja"),
                "items": [
                    {"title": _("Igrejas"), "icon": "church", "link": reverse_lazy("admin:church_church_changelist")},
                    {"title": _("Congregações"), "icon": "location_on",
                     "link": reverse_lazy("admin:church_congregation_changelist")},
                ],
            },
            {
                "title": _("ADMSKIDS"),
                "items": [
                    {"title": _("Crianças"), "icon": "child_care",
                     "link": reverse_lazy("admin:admskids_kid_changelist")},
                    {"title": _("Responsáveis"), "icon": "family_restroom",
                     "link": reverse_lazy("admin:admskids_guardian_changelist")},
                    {"title": _("Turmas"), "icon": "class",
                     "link": reverse_lazy("admin:admskids_kidsclass_changelist")},
                    {"title": _("Sessões"), "icon": "event",
                     "link": reverse_lazy("admin:admskids_classsession_changelist")},
                    {"title": _("Matrículas"), "icon": "how_to_reg",
                     "link": reverse_lazy("admin:admskids_enrollment_changelist")},
                    {"title": _("Presenças"), "icon": "fact_check",
                     "link": reverse_lazy("admin:admskids_kidattendance_changelist")},
                ],
            },
            {
                "title": _("Palavra Pastoral"),
                "items": [
                    {
                        "title": _("Mensagens"),
                        "icon": "campaign",  # ou "record_voice_over", "play_circle", "video_library"
                        "link": reverse_lazy("admin:palavra_pastoral_palavrapastoral_changelist"),
                    },
                ],
            },
            {
                "title": _("Ao Vivo"),
                "items": [
                    {
                        "title": _("Categorias"),
                        "icon": "category",
                        "link": reverse_lazy("admin:aovivo_aovivocategory_changelist"),
                    },
                    {
                        "title": _("Vídeos"),
                        "icon": "video_library",
                        "link": reverse_lazy("admin:aovivo_aovivovideo_changelist"),
                    },
                ],
            },

            # {
            #     "title": _("Tokens JWT"),
            #     "items": [
            #         {"title": _("Outstanding"), "icon": "key", "link": reverse_lazy("admin:token_blacklist_outstandingtoken_changelist")},
            #         {"title": _("Blacklisted"), "icon": "block", "link": reverse_lazy("admin:token_blacklist_blacklistedtoken_changelist")},
            #     ],
            # },
        ],
    },
}

# JWT
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# ----------------------------------------------------------------------------
# CORS
# ----------------------------------------------------------------------------
# For dev: allow all if no explicit origins
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS

# ----------------------------------------------------------------------------
# SECURITY (prod)
# ----------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_REFERRER_POLICY = "same-origin"

    # HSTS: start low; increase gradually after confirming HTTPS is correct.
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ----------------------------------------------------------------------------
# LOGGING (simple)
# ----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
