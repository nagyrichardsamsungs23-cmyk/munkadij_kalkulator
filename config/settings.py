"""
Django settings for Munkadíj Kalkulátor.
Fejlesztői és production (Railway) környezetben is működik.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: productionban környezeti változóból jön
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-x4cskemw9ytsf$*0sb44#8g&b$2et(z$msc)mbocpuumz5i@qn')

# DEBUG: productionban False
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kalkulator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Statikus fájlok production-ben
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Adatbázis: productionban DATABASE_URL-ből (PostgreSQL), fejlesztésben SQLite
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Magyar beállítások
LANGUAGE_CODE = 'hu-HU'
TIME_ZONE = 'Europe/Budapest'
USE_I18N = True
USE_TZ = True

# Statikus fájlok
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise: statikus fájlok tömörítése és cache-elése
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Média fájlok
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# A Railway egy HTTPS-t lezáró proxy mögött futtat: a kérés belül HTTP-ként
# érkezik. E header nélkül a Django nem biztonságosnak hiszi a kérést, ami
# elrontja a CSRF Origin-ellenőrzést és az SSL-redirectet. MINDIG kell.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# A megbízható origin(ek) — a Railway-domaint env-ből vesszük, fallbackkel.
# FONTOS: NEM az `if not DEBUG` blokkban, hogy akkor is működjön, ha a
# DEBUG env változó véletlenül nincs False-ra állítva a Railway-en.
RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
CSRF_TRUSTED_ORIGINS = ['https://munkadijkalkulator-production.up.railway.app']
if RAILWAY_PUBLIC_DOMAIN:
    origin = f'https://{RAILWAY_PUBLIC_DOMAIN}'
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)

# Production security (Railway)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
