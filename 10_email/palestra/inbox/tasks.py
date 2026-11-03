"""Task Celery dell'app inbox."""
from celery import shared_task
from django.core.mail import send_mail  # noqa: F401

from .models import InboundEmail  # noqa: F401


@shared_task
def send_ingest_receipt(email_id):
    """Risponde al mittente con l'esito. Mai a chi e' stato scartato."""
    # TODO (passo 5): 'missing' se l'email non esiste, 'skipped' se e' rejected.
    #   parsed: oggetto 'Luogo aggiunto: <nome>'; unrecognized: 'Email non riconosciuta'
    #   con l'invito a inoltrare un link di Google Maps. send_mail(..., None, [mittente])
    #   usa DEFAULT_FROM_EMAIL. Restituisci 'sent'.
    raise NotImplementedError('TODO passo 5: send_ingest_receipt')
