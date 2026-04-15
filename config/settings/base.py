"""
config/settings/base.py
Configurações base compartilhadas entre todos os ambientes.
"""
import os
from pathlib import Path
import environ

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lê variáveis do .env
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ─────────────────────────────────────────────
# SEGURANÇA
# ─────────────────────────────────────────────
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ─────────────────────────────────────────────
# APLICAÇÕES
# ─────────────────────────────────────────────
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_celery_results",
]

LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.registrations.apps.RegistrationsConfig",
    "apps.certificates.apps.CertificatesConfig",
    "apps.accounts.apps.AccountsConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────
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
                "apps.core.context_processors.company_info",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─────────────────────────────────────────────
# BANCO DE DADOS
# ─────────────────────────────────────────────
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3")
}

# ─────────────────────────────────────────────
# VALIDAÇÃO DE SENHA
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_REDIRECT_URL = "certificates:dashboard"
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ─────────────────────────────────────────────
# INTERNACIONALIZAÇÃO
# ─────────────────────────────────────────────
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# ARQUIVOS ESTÁTICOS E MÍDIA
# ─────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─────────────────────────────────────────────
# E-MAIL
# ─────────────────────────────────────────────
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="certificados@exemplo.com")

# ─────────────────────────────────────────────
# WAHA — WhatsApp API
# ─────────────────────────────────────────────
WAHA_BASE_URL = env("WAHA_BASE_URL", default="http://localhost:3000")
WAHA_API_KEY = env("WAHA_API_KEY", default="")
WAHA_SESSION = env("WAHA_SESSION", default="default")
WAHA_SENDER_NUMBER = env("WAHA_SENDER_NUMBER", default="")
WAHA_ENABLED = env.bool("WAHA_ENABLED", default=False)

# ─────────────────────────────────────────────
# CERTIFICADOS
# ─────────────────────────────────────────────
COMPANY_NAME = env("COMPANY_NAME", default="Minha Empresa")
COMPANY_LOGO_URL = env("COMPANY_LOGO_URL", default="")
CERTIFICATE_BASE_URL = env("CERTIFICATE_BASE_URL", default="http://localhost:8000")

# ─────────────────────────────────────────────
# CELERY
# ─────────────────────────────────────────────
CELERY_BROKER_URL = "redis://127.0.0.1:6379/0"  # Forçado (sem ler do .env) para garantir a conexão
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Em desenvolvimento (o WAHA local precisa acessar o Django local)
WAHA_DJANGO_BASE_URL = "http://127.0.0.1:8000"

# Em produção (Alteração refletindo o novo domínio de produção app.gocertificado.com)
# WAHA_DJANGO_BASE_URL = "https://app.gocertificado.com"
