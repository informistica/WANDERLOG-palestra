import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Tutto ciò che cambia tra ambienti arriva dalle variabili d'ambiente (.env)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

INSTALLED_APPS = [
    'daphne',  # per primo: runserver diventa il server ASGI di Daphne
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # terze parti
    'rest_framework',
    # TODO (passo 1): le app di allauth, prima delle app del progetto
    # app del progetto
    'core',
    'boards',
    'places',
    'inbox',
]

# TODO (passo 1): AccountMiddleware di allauth (in fondo)
# TODO (passo 4): LocaleMiddleware tra SessionMiddleware e CommonMiddleware
# TODO (passo 8): core.middleware.UserLanguageMiddleware dopo AuthenticationMiddleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'palestra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # TODO (passo 3): la cartella templates/ del progetto
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            # TODO (passo 4): il context processor i18n
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'palestra.wsgi.application'

# DATABASE_URL viene letta da dj-database-url
DATABASES = {
    'default': dj_database_url.config(
        default='postgres://user:password@db:5432/palestra_db',
        conn_max_age=600,
    )
}

# Custom user: va impostato prima della prima migrazione
AUTH_USER_MODEL = 'boards.User'

# TODO (passo 1): AUTHENTICATION_BACKENDS con ModelBackend e il backend di allauth

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'it'
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
# TODO (passo 4): LANGUAGES (it, en) e LOCALE_PATHS
USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# API REST (DRF): sessione di Django, accesso solo autenticato, paginazione comune
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.DefaultPagination',
    'PAGE_SIZE': 20,
}

# Pagine HTML (livello 06): login di django.contrib.auth sotto /accounts/
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'boards:list'
LOGOUT_REDIRECT_URL = 'login'
# TODO (passo 2): URL di allauth nei redirect e impostazioni ACCOUNT_* (login con email)

# Celery (livello 08): broker e risultati su Redis, messaggi solo in JSON
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Channels (livello 09): Django come applicazione ASGI, gruppi su Redis
ASGI_APPLICATION = 'palestra.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [os.environ.get('CHANNEL_LAYER_URL', 'redis://redis:6379/1')]},
    },
}

# Email (livello 10): in sviluppo la posta in uscita finisce in Mailpit
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'mailpit')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '1025'))
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@palestra.local')
# Dominio degli indirizzi delle bacheche: board+<token>@INBOUND_EMAIL_DOMAIN
INBOUND_EMAIL_DOMAIN = os.environ.get('INBOUND_EMAIL_DOMAIN', 'palestra.local')
