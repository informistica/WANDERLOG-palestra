"""Task Celery dell'app places."""
from celery import shared_task

from . import geocoding  # noqa: F401
from .models import Place  # noqa: F401


# TODO (passo 3): ritenta in automatico su geocoding.GeocodingError,
#   con attesa crescente (retry_backoff) e al massimo 5 tentativi
@shared_task
def geocode_place(place_id):
    """Completa l'indirizzo di un luogo. Idempotente: rieseguirlo non rifa' il lavoro."""
    # TODO (passo 3): cerca il luogo per id ('missing' se non c'e' piu');
    #   se ha gia' un indirizzo restituisci 'skipped';
    #   altrimenti chiama geocoding.reverse_geocode, salva solo address e updated_at
    #   e restituisci 'done'
    raise NotImplementedError
