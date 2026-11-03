"""Test di controllo dell'ambiente: dipendono da .env e dai servizi avviati, non dai TODO."""
import os
from io import StringIO

import pytest

LEVEL_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_env_file_exists():
    """Il file .env esiste nella cartella del livello (accanto a compose.yaml)."""
    assert os.path.exists(os.path.join(LEVEL_ROOT, '.env')), (
        "Il file .env non esiste. Copia .env.example in .env e configura DJANGO_SECRET_KEY"
    )


def test_secret_key_configured():
    """DJANGO_SECRET_KEY è impostata e non è il valore di esempio."""
    secret_key = os.environ.get('DJANGO_SECRET_KEY', '')
    assert secret_key != '', "DJANGO_SECRET_KEY non è configurata nel file .env"
    assert 'change-me' not in secret_key.lower(), (
        "DJANGO_SECRET_KEY ha ancora il valore di esempio. Genera una chiave sicura!"
    )
    assert len(secret_key) >= 50, "DJANGO_SECRET_KEY deve essere lunga almeno 50 caratteri"


@pytest.mark.django_db
def test_database_connection():
    """Django si connette a PostgreSQL."""
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1
    assert connection.vendor == 'postgresql', "Il database deve essere PostgreSQL (DATABASE_URL)"


def test_redis_connection():
    """Redis risponde al ping."""
    import redis
    r = redis.from_url(os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
    try:
        assert r.ping()
    except Exception as e:  # noqa: BLE001
        pytest.fail(f"Impossibile connettersi a Redis: {e}")


def test_django_check():
    """manage.py check non segnala errori."""
    from django.core.management import call_command
    out = StringIO()
    call_command('check', stdout=out, stderr=out)
    assert 'System check identified no issues' in out.getvalue()
