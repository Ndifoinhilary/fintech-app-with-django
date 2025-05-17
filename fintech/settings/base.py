from datetime import date
from os import getenv
from pathlib import Path

import cloudinary
from dotenv import load_dotenv
from loguru import logger

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

APPS_DIR = BASE_DIR / 'apps'
local_env_file = BASE_DIR / "fintech" / ".envs" / ".env.local"
if local_env_file.is_file():
    load_dotenv(dotenv_path=local_env_file)

# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'django_countries',
    'django_celery_beat',
    'djoser',
    'drf_spectacular',
    'djcelery_email',
    'cloudinary',
    'flower',
    'phonenumber_field',
]
LOCAL_APPS = ["apps.core", "apps.account"]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.account.middleware.CustomHeaderMiddleware'
]

ROOT_URLCONF = 'fintech.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR / 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fintech.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('POSTGRES_DB'),
        'USER': getenv('POSTGRES_USER'),
        'PASSWORD': getenv('POSTGRES_PASSWORD'),
        'HOST': getenv('POSTGRES_HOST'),
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING_CONFIG = None

LOGURU_LOGGING = {
    "handlers": [
        {"sink": BASE_DIR / "logs/debug.log",
         "level": "DEBUG",
         "filter": lambda record: record["level"].no <= logger.level("WARNING").no,
         "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
         "rotation": "10MB",
         "retention": "30 days",
         "compression": "zip",
         },
        {"sink": BASE_DIR / "logs/error.log",
         "level": "ERROR",
         "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{module}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
         "rotation": "10MB",
         "retention": "30 days",
         "compression": "zip",
         "backtrace": True,
         "diagnose": True,
         },

    ],
}

CLOUDINARY_CLOUD_NAME = getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = getenv('CLOUDINARY_API_SECRET')

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

logger.configure(**LOGURU_LOGGING)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"loguru": {"class": "interceptor.InterceptHandler"}},
    "root": {
        "handlers": ["loguru"],
        "level": "DEBUG",
    },
}

AUTH_USER_MODEL = 'account.User'
DEFAULT_BIRTH_DATE = date(1900, 1, 1)
DEFAULT_DATE= date(2000, 1, 1)
DEFAULT_EXPIRY_DATE= date(20224, 1, 1)
DEFAULT_COUNTRY = "CM"
DEFAULT_PHONE_NUMBER = "+237650282777"
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Settings for drf spectacular
SPECTACULAR_SETTINGS = {
    "TITLE": "Fintech API",
    "DESCRIPTION": "Fintech API documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "LICENSE": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
}

# Celery settings
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = getenv("CELERY_BROKER_URL")
CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND")
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_TASK_SENT_EVENT = True
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULE = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True


# Setting up cookies
COOKIE_NAME="access"
COOKIE_SAMESITE = "Lax"
COOKIE_PATH="/"
COOKIE_SECURE = getenv("COOKIE_SECURE", "True") == "True"
COOKIE_HTTPONLY = True