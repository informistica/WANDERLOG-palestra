"""Service layer dell'app inbox: da un file .eml a un luogo sulla bacheca."""
import re
from email import message_from_bytes, policy
from email.utils import getaddresses, parseaddr

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from boards.policies import can_view_board
from places.services import add_place_to_board

from .models import InboundAddress, InboundEmail
from .tasks import send_ingest_receipt

_PAIR = r'(-?\d{1,3}(?:\.\d+)?)\s*(?:,|%2C)\s*(-?\d{1,3}(?:\.\d+)?)'
COORDINATE_PATTERNS = [
    re.compile(r'@' + _PAIR),                        # google.com/maps/place/Nome/@41.89,12.49,17z
    re.compile(r'[?&](?:q|query|ll)=' + _PAIR),      # maps.google.com/?q=41.89,12.49
    re.compile(r'\bgeo:' + _PAIR),                   # geo:41.89,12.49 (RFC 5870)
]
SUBJECT_PREFIX = re.compile(r'^\s*(?:(?:fwd?|i|r|re|tr)\s*:\s*)+', re.IGNORECASE)
DEFAULT_NAME = 'Luogo da email'


def address_for_board(board):
    """L'indirizzo a cui inoltrare le email per `board`. Lo crea alla prima richiesta."""
    inbound, _ = InboundAddress.objects.get_or_create(board=board)
    return f'board+{inbound.token}@{settings.INBOUND_EMAIL_DOMAIN}'


def board_from_recipient(address):
    """La bacheca di un indirizzo board+<token>@dominio, oppure None."""
    _, addr = parseaddr(address or '')
    local, at, domain = addr.rpartition('@')
    if not at or domain.lower() != settings.INBOUND_EMAIL_DOMAIN.lower():
        return None
    prefix, plus, token = local.partition('+')
    if prefix.lower() != 'board' or not plus or not token:
        return None
    inbound = InboundAddress.objects.select_related('board').filter(token=token.lower()).first()
    return inbound.board if inbound else None


def parse_coordinates(text):
    """Le prime coordinate valide (lat, lng) trovate in un link di mappa, oppure None."""
    for pattern in COORDINATE_PATTERNS:
        for match in pattern.finditer(text or ''):
            lat, lng = float(match.group(1)), float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
    return None


def _body_text(message):
    part = message.get_body(preferencelist=('plain', 'html'))
    return part.get_content() if part is not None else ''


@transaction.atomic
def ingest_eml(raw):
    """Elabora un'email grezza (bytes) e restituisce l'InboundEmail salvata."""
    message = message_from_bytes(raw, policy=policy.default)
    message_id = str(message.get('Message-ID', '')).strip()[:255]
    if message_id:
        existing = InboundEmail.objects.filter(message_id=message_id).first()
        if existing is not None:
            return existing  # la stessa email consegnata due volte: niente doppioni

    sender = parseaddr(str(message.get('From', '')))[1].lower()
    subject = str(message.get('Subject', '')).strip()
    headers = [str(h) for h in message.get_all('To', []) + message.get_all('Cc', [])]
    recipients = [addr for _, addr in getaddresses(headers) if addr]
    record = InboundEmail(sender=sender[:255], subject=subject[:255], message_id=message_id,
                          recipient=', '.join(recipients)[:255])

    board = next((b for b in map(board_from_recipient, recipients) if b is not None), None)
    if board is None:
        record.status, record.reason = InboundEmail.STATUS_REJECTED, 'indirizzo della bacheca sconosciuto'
        record.save()
        return record  # a chi non conosciamo non rispondiamo (backscatter)
    record.board = board

    user = get_user_model().objects.filter(email__iexact=sender).first() if sender else None
    if not can_view_board(user, board):
        record.status, record.reason = InboundEmail.STATUS_REJECTED, 'mittente non autorizzato'
        record.save()
        return record

    coordinates = parse_coordinates(subject + '\n' + _body_text(message))
    if coordinates is None:
        record.status, record.reason = InboundEmail.STATUS_UNRECOGNIZED, 'nessuna coordinata trovata'
    else:
        name = SUBJECT_PREFIX.sub('', subject).strip()[:255] or DEFAULT_NAME
        record.place = add_place_to_board(board, name, *coordinates,
                                          description=f'Aggiunto via email da {sender}')
        record.status = InboundEmail.STATUS_PARSED
    record.save()
    # la ricevuta parte solo se il luogo e l'email sono davvero nel database
    transaction.on_commit(lambda: send_ingest_receipt.delay(str(record.id)))
    return record
