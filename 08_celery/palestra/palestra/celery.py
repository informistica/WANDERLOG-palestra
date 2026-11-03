"""App Celery del progetto. Il worker si avvia con `celery -A palestra worker -l info`."""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'palestra.settings')

app = Celery('palestra')
# TODO (passo 2): leggi la configurazione dalle impostazioni di Django con prefisso CELERY_
# TODO (passo 2): fai trovare all'app i moduli tasks.py delle app installate
