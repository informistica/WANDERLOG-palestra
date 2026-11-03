"""Task Celery dell'app places."""
from celery import shared_task

from . import geocoding
from .models import Place


@shared_task(autoretry_for=(geocoding.GeocodingError,), retry_backoff=True, max_retries=5)
def geocode_place(place_id):
    """Completa l'indirizzo di un luogo. Idempotente: rieseguirlo non rifa' il lavoro."""
    place = Place.objects.filter(pk=place_id).first()
    if place is None:
        return 'missing'  # cancellato prima che il worker arrivasse
    if place.address:
        return 'skipped'
    place.address = geocoding.reverse_geocode(place.lat, place.lng)
    place.save(update_fields=['address', 'updated_at'])
    return 'done'
