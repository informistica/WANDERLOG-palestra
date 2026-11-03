"""App Celery del progetto. Il worker si avvia con `celery -A palestra worker -l info`."""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'palestra.settings')

app = Celery('palestra')
# Le impostazioni CELERY_* di settings.py diventano la configurazione dell'app
app.config_from_object('django.conf:settings', namespace='CELERY')
# Cerca un modulo tasks.py in ogni app di INSTALLED_APPS
app.autodiscover_tasks()
