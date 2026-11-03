"""Task Celery dell'app inbox."""
from celery import shared_task
from django.core.mail import send_mail

from .models import InboundEmail


@shared_task
def send_ingest_receipt(email_id):
    """Risponde al mittente con l'esito. Mai a chi e' stato scartato."""
    record = InboundEmail.objects.select_related('board', 'place').filter(pk=email_id).first()
    if record is None:
        return 'missing'
    if record.status == InboundEmail.STATUS_REJECTED or not record.sender:
        return 'skipped'
    if record.status == InboundEmail.STATUS_PARSED:
        name = record.place.name if record.place else record.subject
        subject = f'Luogo aggiunto: {name}'
        body = f'Ho aggiunto "{name}" alla bacheca "{record.board.title}".'
    else:
        subject = 'Email non riconosciuta'
        body = ('Non ho trovato coordinate nella tua email. '
                'Inoltra un link di Google Maps (con @lat,lng o ?q=lat,lng) oppure un link geo:.')
    send_mail(subject, body, None, [record.sender])
    return 'sent'
