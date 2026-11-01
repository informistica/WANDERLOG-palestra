SECRET_KEY = 'test-key'
DEBUG = True
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'core',
    'boards',
    'places',
]
AUTH_USER_MODEL = 'boards.User'
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
