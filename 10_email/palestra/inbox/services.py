"""Service layer dell'app inbox: da un file .eml a un luogo sulla bacheca."""
import re  # noqa: F401
from email import message_from_bytes, policy  # noqa: F401
from email.utils import getaddresses, parseaddr  # noqa: F401

from django.conf import settings  # noqa: F401
from django.contrib.auth import get_user_model  # noqa: F401
from django.db import transaction  # noqa: F401

from boards.policies import can_view_board  # noqa: F401
from places.services import add_place_to_board  # noqa: F401

from .models import InboundAddress, InboundEmail  # noqa: F401
from .tasks import send_ingest_receipt  # noqa: F401

DEFAULT_NAME = 'Luogo da email'


def address_for_board(board):
    """L'indirizzo a cui inoltrare le email per `board`. Lo crea alla prima richiesta."""
    # TODO (passo 2): get_or_create dell'InboundAddress della bacheca, poi
    #   'board+<token>@<settings.INBOUND_EMAIL_DOMAIN>'
    raise NotImplementedError('TODO passo 2: address_for_board')


def board_from_recipient(address):
    """La bacheca di un indirizzo board+<token>@dominio, oppure None."""
    # TODO (passo 2): parseaddr toglie il nome ("Roma <board+...@...>").
    #   Dominio uguale a INBOUND_EMAIL_DOMAIN e parte locale 'board+<token>',
    #   senza badare alle maiuscole. Altrimenti None.
    raise NotImplementedError('TODO passo 2: board_from_recipient')


def parse_coordinates(text):
    """Le prime coordinate valide (lat, lng) trovate in un link di mappa, oppure None."""
    # TODO (passo 3): espressioni regolari per '@lat,lng', '?q=lat,lng' (anche query= e
    #   la virgola scritta %2C) e 'geo:lat,lng'. Scarta latitudini e longitudini fuori scala.
    raise NotImplementedError('TODO passo 3: parse_coordinates')


def ingest_eml(raw):
    """Elabora un'email grezza (bytes) e restituisce l'InboundEmail salvata."""
    # TODO (passo 4): message_from_bytes(raw, policy=policy.default), poi in ordine:
    #   - Message-ID gia' visto: restituisci l'InboundEmail esistente
    #   - nessun destinatario (To o Cc) e' una bacheca: STATUS_REJECTED
    #   - il mittente non puo' vedere la bacheca (can_view_board): STATUS_REJECTED
    #   - nessuna coordinata nell'oggetto o nel corpo: STATUS_UNRECOGNIZED
    #   - altrimenti add_place_to_board con il nome preso dall'oggetto senza 'Fwd:'/'I:'
    #     e STATUS_PARSED
    # TODO (passo 5): solo per parsed e unrecognized, dopo il commit,
    #   send_ingest_receipt.delay(str(record.id))
    raise NotImplementedError('TODO passo 4: ingest_eml')
