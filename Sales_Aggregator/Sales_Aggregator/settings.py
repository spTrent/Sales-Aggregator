"""
Django settings for Sales_Aggregator project.
"""

from pathlib import Path
from typing import Any

BASE_DIR: Path = Path(__file__).resolve().parent.parent

SECRET_KEY: str = (
    'django-insecure-j^%33z#05@p(5no%8cw!8*mn%kdk%8q+ny&pieg_k4pvh16p!^'
)

DEBUG: bool = True

ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS: list[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'discounts',
]

MIDDLEWARE: list[str] = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF: str = 'Sales_Aggregator.urls'

TEMPLATES: list[dict[str, Any]] = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION: str = 'Sales_Aggregator.wsgi.application'

DATABASES: dict[str, dict[str, str]] = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sales_aggregator_db',
        'USER': 'sales_user',
        'PASSWORD': 'qwerty123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
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

LANGUAGE_CODE: str = 'en-us'
TIME_ZONE: str = 'UTC'
USE_I18N: bool = True
USE_TZ: bool = True

STATIC_URL: str = 'static/'

DEFAULT_AUTO_FIELD: str = 'django.db.models.BigAutoField'

AUTH_USER_MODEL: str = 'users.CustomUser'

LOGIN_REDIRECT_URL: str = 'home'
LOGOUT_REDIRECT_URL: str = 'home'

MEDIA_URL: str = '/media/'
MEDIA_ROOT: Path = BASE_DIR / 'media'
