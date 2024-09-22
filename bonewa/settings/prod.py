import os

# from bonewa.settings.base import BASE_DIR
from .base import BASE_DIR

DEBUG = False
ALLOWED_HOSTS = ["dev.bonewa.com"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# DEFAULT_FROM_EMAIL = "hellobhai05@gmail.com"
STATIC_URL = "static/"
