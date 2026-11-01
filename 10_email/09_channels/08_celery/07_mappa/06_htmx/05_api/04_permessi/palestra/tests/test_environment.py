"""Test per verificare la configurazione dell'ambiente Docker Compose."""
import os
import subprocess
import pytest


def test_env_file_exists():
    """Verifica che il file .env esista (nella directory parent)."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    assert os.path.exists(env_path), (
        "Il file .env non esiste. Copia .env.example in .env e configura DJANGO_SECRET_KEY"
    )


def test_secret_key_configured():
    """Verifica che SECRET_KEY sia configurata e non sia il valore di default."""
    secret_key = os.environ.get('DJANGO_SECRET_KEY', '')
    assert secret_key != '', "DJANGO_SECRET_KEY non è configurata nel file .env"
    assert 'change-me' not in secret_key.lower(), (
        "DJANGO_SECRET_KEY ha ancora il valore di default. Genera una chiave sicura!"
    )
    assert len(secret_key) >= 50, "DJANGO_SECRET_KEY deve essere lunga almeno 50 caratteri"


def test_database_connection():
    """Verifica che Django possa connettersi al database PostgreSQL."""
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1, "Query di test al database fallita"
    except Exception as e:
        pytest.fail(f"Impossibile connettersi al database: {e}")


def test_redis_connection():
    """Verifica che Redis sia raggiungibile."""
    import redis
    redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    try:
        r = redis.from_url(redis_url)
        r.ping()
    except Exception as e:
        pytest.fail(f"Impossibile connettersi a Redis: {e}")


def test_django_check():
    """Verifica che manage.py check non mostri errori."""
    import django
    from django.core.management import call_command
    from io import StringIO
    
    django.setup()
    
    out = StringIO()
    try:
        call_command('check', stdout=out, stderr=out)
        output = out.getvalue()
        # Non deve contenere errori critici
        assert 'Error' not in output or 'System check identified no issues' in output
    except Exception as e:
        pytest.fail(f"django check ha fallito: {e}")
