"""
config/settings/development.py
"""
from .base import *  # noqa

import sys

DEBUG = True

# Evita erro debug_toolbar.E001 durante testes
if "test" not in sys.argv:
    INSTALLED_APPS += ["debug_toolbar"]  # noqa
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE  # noqa

INTERNAL_IPS = ["127.0.0.1"]

# E-mail no console durante dev
#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Permite qualquer host em dev
ALLOWED_HOSTS = ["*"]
