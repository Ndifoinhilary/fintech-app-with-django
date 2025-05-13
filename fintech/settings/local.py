
from .base import  *


APPS_DIR = BASE_DIR / 'apps'
local_env_file = BASE_DIR / "fintech" / ".envs" / ".env.local"
if local_env_file.is_file():
    load_dotenv(dotenv_path=local_env_file)


SECRET_KEY = getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DEBUG")

SITE_NAME = getenv("SITE_NAME")

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
ADMIN_URL = getenv("ADMIN_URL")

EMAIL_BACKEND = 'django.core.mail.backends.CeleryEmailBackend'
EMAIL_HOST = getenv("EMAIL_HOST")
EMAIL_PORT = getenv("EMAIL_PORT")
DEFAULT_FROM_EMAIL = getenv("DEFAULT_FROM_EMAIL")
DOMAIN_NAME = getenv("DOMAIN_NAME")

MAX_UPLOAD_SIZE = 1 * 1024 * 1024




CSRF_TRUSTED_ORIGINS = ['http://localhost:8000']

LOGIN_ATTEMPTS_LIMIT = 3
LOCKOUT_DURATION= timedelta(minutes=1)
OTP_EXPIRATION_TIME = timedelta(minutes=1)


