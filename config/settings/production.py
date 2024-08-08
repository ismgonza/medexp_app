import os
from config.settings.base import *
from dotenv import load_dotenv
from config.logging import *

# Load environment variables from .env file
load_dotenv(Path.joinpath(BASE_DIR, '.env_prod'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000  # 1 year
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True

ALLOWED_HOSTS = ['portal.vgclinic.com', '*']
# CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://portal.vgclinic.com']
# USE_X_FORWARDED_HOST = True


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', default=''),
        'USER': os.getenv('DB_USER', default=''),
        'PASSWORD': os.getenv('DB_PASSWORD', default=''),
        'HOST': os.getenv('DB_HOST', default=''),
        'PORT': os.getenv('DB_PORT', default=''),
        'CONN_MAX_AGE': 600,  # connection persistence for 10 minutes
        # 'OPTIONS': {
        #     'connect_timeout': 5,
        # }
    }
}

STATIC_ROOT = Path.joinpath(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    Path.joinpath(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CHECK FOR STORAGE
# https://docs.djangoproject.com/en/5.0/ref/settings/#std-setting-STORAGES
