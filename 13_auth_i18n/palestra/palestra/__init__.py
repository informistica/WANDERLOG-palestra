# L'app Celery si carica insieme a Django, cosi' @shared_task usa questa app
from .celery import app as celery_app

__all__ = ('celery_app',)
