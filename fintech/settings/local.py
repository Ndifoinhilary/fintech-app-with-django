from os import getenv, path
from dotenv import  load_dotenv
from .base import  *

APPS_DIR = BASE_DIR / 'apps'
local_env_files = path.join(BASE_DIR, ".envs", ".env.local")

if path.isfile(local_env_files):
    load_dotenv(local_env_files)


SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG")

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']
ADMIN_URL = getenv("ADMIN_URL")

EMAIL_BACKEND = 'django.core.mail.backends.console.CeleryEmailBackend'
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
DOMAIN_NAME = getenv("DOMAIN_NAME")

MAX_UPLOAD_SIZE = 1 * 1024 * 1024




