"""Livello 10: luoghi aggiunti inoltrando un'email alla bacheca."""
import os
import uuid
from io import StringIO
from pathlib import Path

import pytest
import yaml
from django.conf import settings as django_settings
from django.core import mail
from django.core.management import CommandError, call_command

from boards.models import Board, Collaborator, User
from inbox import services
from inbox.models import InboundAddress, InboundEmail
from inbox.tasks import send_ingest_receipt
from places.models import Place

LEVEL_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURES = Path(__file__).resolve().parent / 'fixtures' / 'emails'
TOKEN = 'colosseo42'
DOMAIN = os.environ.get('INBOUND_EMAIL_DOMAIN', 'palestra.local')


def eml(name):
    return (FIXTURES / name).read_bytes()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@example.com', password='pass12345')


@pytest.fixture
def viewer(db):
    return User.objects.create_user(email='viewer@example.com', password='pass12345')


@pytest.fixture
def stranger(db):
    return User.objects.create_user(email='stranger@example.com', password='pass12345')


@pytest.fixture
def board(owner, viewer):
    board = Board.objects.create(title='Roma', owner=owner)
    Collaborator.objects.create(board=board, user=viewer)
    InboundAddress.objects.create(board=board, token=TOKEN)
    return board


class TestConfig:
    """Passo 1: impostazioni e Mailpit."""

    def test_email_settings_from_environment(self):
        assert django_settings.DEFAULT_FROM_EMAIL == os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@palestra.local')
        assert django_settings.INBOUND_EMAIL_DOMAIN == DOMAIN
        assert django_settings.EMAIL_HOST == os.environ.get('EMAIL_HOST', 'mailpit')
        assert django_settings.EMAIL_PORT == int(os.environ.get('EMAIL_PORT', '1025'))

    def test_compose_mailpit(self):
        with open(LEVEL_ROOT / 'compose.yaml', encoding='utf-8') as f:
            services_ = yaml.safe_load(f)['services']
        mailpit = services_.get('mailpit')
        assert mailpit, 'manca il servizio mailpit'
        assert mailpit['image'].startswith('axllent/mailpit')
        ports = [str(p) for p in mailpit.get('ports', [])]
        assert any(p.endswith(':8025') for p in ports), 'interfaccia web su 8025'
        assert any(p.endswith(':1025') for p in ports), 'SMTP su 1025'
        assert 'mailpit' in (services_['django'].get('depends_on') or {})
        assert 'mailpit' in (services_['celery-worker'].get('depends_on') or {})


@pytest.mark.django_db
class TestAddress:
    """Passo 2: l'indirizzo board+<token>@dominio."""

    def test_address_for_board(self, board, owner):
        assert services.address_for_board(board) == f'board+{TOKEN}@{DOMAIN}'
        other = Board.objects.create(title='Milano', owner=owner)
        address = services.address_for_board(other)
        assert address == services.address_for_board(other), "l'indirizzo non cambia a ogni chiamata"
        token = InboundAddress.objects.get(board=other).token
        assert address == f'board+{token}@{DOMAIN}' and len(token) >= 16 and token != TOKEN

    @pytest.mark.parametrize('address, found', [
        ('board+{t}@{d}', True),
        ('Roma <Board+{T}@{D}>', True),
        ('board+{t}@altro.example', False),
        ('board+sconosciuto@{d}', False),
        ('{t}@{d}', False),
        ('', False),
    ])
    def test_board_from_recipient(self, board, address, found):
        address = address.format(t=TOKEN, T=TOKEN.upper(), d=DOMAIN, D=DOMAIN.upper())
        result = services.board_from_recipient(address)
        if found:
            assert result == board
        else:
            assert result is None


class TestParseCoordinates:
    """Passo 3: coordinate dai link di mappa."""

    @pytest.mark.parametrize('text, expected', [
        ('https://www.google.com/maps/place/Colosseo/@41.8902102,12.4922309,17z', (41.8902102, 12.4922309)),
        ('https://maps.google.com/?q=41.8986,12.4769', (41.8986, 12.4769)),
        ('https://www.google.com/maps/search/?api=1&query=41.8986%2C12.4769', (41.8986, 12.4769)),
        ('geo:45.4642,9.19', (45.4642, 9.19)),
        ('Sydney: https://www.google.com/maps/@-33.8568,151.2153,15z', (-33.8568, 151.2153)),
        ('scrivimi a owner@example.com, alle 12,30', None),
        ('https://www.google.com/maps/@95.0,12.0,15z', None),
        ('nessun link qui', None),
    ])
    def test_parse(self, text, expected):
        result = services.parse_coordinates(text)
        if expected is None:
            assert result is None
        else:
            assert result == pytest.approx(expected)


@pytest.mark.django_db
class TestIngest:
    """Passo 4: dal file .eml al luogo."""

    def test_owner_link_creates_place(self, board):
        record = services.ingest_eml(eml('owner_maps_link.eml'))
        assert record.status == InboundEmail.STATUS_PARSED
        assert record.sender == 'owner@example.com' and record.board == board
        place = record.place
        assert place.board == board and place.name == 'Colosseo', "il nome e' l'oggetto senza 'Fwd:'"
        assert (place.lat, place.lng) == pytest.approx((41.8902102, 12.4922309))
        assert Place.objects.filter(board=board).count() == 1

    def test_collaborator_html_in_cc(self, board):
        record = services.ingest_eml(eml('collaborator_html.eml'))
        assert record.status == InboundEmail.STATUS_PARSED, 'il collaboratore puo\' aggiungere luoghi'
        assert record.sender == 'viewer@example.com'
        assert record.place.name == 'Pantheon'
        assert (record.place.lat, record.place.lng) == pytest.approx((41.8986, 12.4769))

    def test_encoded_subject_and_base64_body(self, board):
        record = services.ingest_eml(eml('encoded_base64.eml'))
        assert record.status == InboundEmail.STATUS_PARSED
        assert record.place.name == 'Caffè Florian'

    def test_sender_case_and_geo_uri(self, board):
        record = services.ingest_eml(eml('owner_geo_uppercase.eml'))
        assert record.status == InboundEmail.STATUS_PARSED
        assert record.place.name == 'Duomo di Milano'
        assert (record.place.lat, record.place.lng) == pytest.approx((45.4642, 9.19))

    @pytest.mark.parametrize('fixture', ['stranger.eml', 'unknown_sender.eml', 'unknown_address.eml'])
    def test_rejected(self, board, stranger, fixture):
        record = services.ingest_eml(eml(fixture))
        assert record.status == InboundEmail.STATUS_REJECTED and record.reason
        assert record.place is None
        assert Place.objects.count() == 0
        assert InboundEmail.objects.count() == 1, "anche le email scartate restano tracciate"

    def test_no_coordinates_is_unrecognized(self, board):
        record = services.ingest_eml(eml('no_coordinates.eml'))
        assert record.status == InboundEmail.STATUS_UNRECOGNIZED and record.reason
        assert record.board == board and record.place is None
        assert Place.objects.count() == 0

    def test_same_message_id_only_once(self, board):
        first = services.ingest_eml(eml('owner_maps_link.eml'))
        second = services.ingest_eml(eml('owner_maps_link.eml'))
        assert first.pk == second.pk
        assert Place.objects.count() == 1 and InboundEmail.objects.count() == 1


@pytest.mark.django_db
class TestReceipt:
    """Passo 5: la ricevuta via Celery, dopo il commit."""

    def test_receipt_after_commit(self, board, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks() as callbacks:
            services.ingest_eml(eml('owner_maps_link.eml'))
        assert mail.outbox == [], 'prima del commit non parte niente'
        for callback in callbacks:
            callback()
        assert len(mail.outbox) == 1
        message = mail.outbox[0]
        assert message.to == ['owner@example.com']
        assert 'Colosseo' in message.subject
        assert message.from_email == django_settings.DEFAULT_FROM_EMAIL

    def test_unrecognized_gets_help(self, board, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks(execute=True):
            services.ingest_eml(eml('no_coordinates.eml'))
        assert len(mail.outbox) == 1
        assert 'non riconosciuta' in mail.outbox[0].subject.lower()
        assert 'Google Maps' in mail.outbox[0].body

    def test_rejected_gets_no_reply(self, board, stranger, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks(execute=True):
            record = services.ingest_eml(eml('stranger.eml'))
        assert record.status == InboundEmail.STATUS_REJECTED
        assert mail.outbox == [], 'a chi non e\' autorizzato non si risponde'
        assert send_ingest_receipt(str(record.id)) == 'skipped'

    def test_task_missing_email(self):
        assert send_ingest_receipt(str(uuid.uuid4())) == 'missing'


@pytest.mark.django_db
class TestCommand:
    """Passo 6: il comando ingest_eml."""

    def test_ingest_command(self, board):
        out = StringIO()
        call_command('ingest_eml', str(FIXTURES / 'owner_maps_link.eml'),
                     str(FIXTURES / 'no_coordinates.eml'), stdout=out)
        text = out.getvalue()
        assert 'owner_maps_link.eml: parsed' in text and 'Colosseo' in text
        assert 'no_coordinates.eml: unrecognized' in text
        assert Place.objects.filter(board=board).count() == 1

    def test_missing_file(self, board):
        with pytest.raises(CommandError):
            call_command('ingest_eml', str(FIXTURES / 'non-esiste.eml'))