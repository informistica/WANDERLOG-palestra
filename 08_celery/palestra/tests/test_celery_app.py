"""Livello 08: l'app Celery, la sua configurazione e il worker."""
import os
import subprocess
import sys

import yaml
from django.conf import settings

from palestra.celery import app

PROJECT_DIR = settings.BASE_DIR
LEVEL_ROOT = os.path.dirname(PROJECT_DIR)


class TestCeleryConfig:
    """Passi 1-2: impostazioni e app."""

    def test_settings_from_environment(self):
        assert settings.CELERY_BROKER_URL == os.environ['CELERY_BROKER_URL']
        assert settings.CELERY_RESULT_BACKEND == os.environ['REDIS_URL']
        assert settings.CELERY_ACCEPT_CONTENT == ['json']
        assert settings.CELERY_TASK_SERIALIZER == 'json'
        assert settings.CELERY_RESULT_SERIALIZER == 'json'

    def test_app_reads_django_settings(self):
        assert app.main == 'palestra'
        assert app.conf.broker_url == settings.CELERY_BROKER_URL
        assert app.conf.result_backend == settings.CELERY_RESULT_BACKEND
        assert app.conf.task_serializer == 'json'

    def test_project_exposes_celery_app(self):
        import palestra
        assert getattr(palestra, 'celery_app', None) is app
        assert 'celery_app' in getattr(palestra, '__all__', ())

    def test_broker_is_reachable(self):
        # Celery legge da solo la variabile CELERY_BROKER_URL: il confronto con settings
        # verifica che la configurazione arrivi da Django
        assert app.conf.broker_url == settings.CELERY_BROKER_URL
        assert app.conf.broker_url.startswith('redis://'), 'il broker e\' Redis'
        with app.connection_for_write() as conn:
            conn.ensure_connection(max_retries=1)

    def test_worker_discovers_tasks(self):
        # Come fa il worker: un processo nuovo che carica Django e cerca i tasks.py
        code = ('import django; django.setup(); from palestra.celery import app; '
                'app.loader.import_default_modules(); print(app.conf.result_backend); '
                'print(*sorted(n for n in app.tasks if not n.startswith("celery.")))')
        env = dict(os.environ, DJANGO_SETTINGS_MODULE='palestra.settings')
        out = subprocess.run([sys.executable, '-c', code], cwd=PROJECT_DIR, env=env,
                             capture_output=True, text=True, timeout=120)
        assert out.returncode == 0, out.stderr[-1500:]
        backend, _, names = out.stdout.partition('\n')
        assert backend.strip() == os.environ['REDIS_URL'], 'il worker usa la configurazione di Django'
        assert 'places.tasks.geocode_place' in names.split()


class TestComposeWorker:
    """Passo 5: il servizio celery-worker nel compose."""

    def test_worker_service(self):
        with open(os.path.join(LEVEL_ROOT, 'compose.yaml'), encoding='utf-8') as f:
            services = yaml.safe_load(f)['services']
        worker = services.get('celery-worker')
        assert worker, 'manca il servizio celery-worker'
        command = worker.get('command')
        command = ' '.join(command) if isinstance(command, list) else (command or '')
        assert 'celery -A palestra worker' in command
        env_file = worker.get('env_file')
        files = [env_file] if isinstance(env_file, str) else (env_file or [])
        assert '.env' in [f if isinstance(f, str) else f.get('path') for f in files]
        depends = worker.get('depends_on') or {}
        assert 'redis' in depends and 'db' in depends
        assert worker.get('working_dir') == services['django'].get('working_dir')
        assert 'ports' not in worker, 'il worker non serve richieste HTTP'
