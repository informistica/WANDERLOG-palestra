"""Livello 08: il task geocode_place, l'idempotenza e la chiamata dal service layer."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from boards.models import Board
from places import geocoding, tasks
from places.models import Place
from places.services import add_place_to_board
from places.tasks import geocode_place

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@example.com', password='test12345')


@pytest.fixture
def board(owner):
    return Board.objects.create(title='Roma', owner=owner)


@pytest.fixture
def place(board):
    return Place.objects.create(board=board, name='Colosseo', lat=41.8902, lng=12.4922)


@pytest.fixture
def calls(monkeypatch):
    """Conta le chiamate al provider di geocodifica."""
    seen = []
    original = geocoding.reverse_geocode

    def fake(lat, lng):
        seen.append((lat, lng))
        return original(lat, lng)

    monkeypatch.setattr(geocoding, 'reverse_geocode', fake)
    return seen


@pytest.mark.django_db
class TestGeocodeTask:
    """Passo 3: il task."""

    def test_sets_address(self, place):
        assert geocode_place(str(place.id)) == 'done'
        place.refresh_from_db()
        assert place.address == 'Indirizzo simulato (41.8902, 12.4922)'

    def test_is_idempotent(self, place, calls):
        assert geocode_place(str(place.id)) == 'done'
        assert geocode_place(str(place.id)) == 'skipped'
        assert len(calls) == 1, 'la seconda esecuzione non deve richiamare il provider'

    def test_keeps_existing_address(self, place, calls):
        place.address = 'Piazza del Colosseo, Roma'
        place.save()
        assert geocode_place(str(place.id)) == 'skipped'
        place.refresh_from_db()
        assert place.address == 'Piazza del Colosseo, Roma'
        assert calls == []

    def test_missing_place(self, place):
        place_id = str(place.id)
        place.delete()
        assert geocode_place(place_id) == 'missing'

    def test_delay_runs_eagerly_in_tests(self, place):
        assert geocode_place.delay(str(place.id)).get(timeout=5) == 'done'
        place.refresh_from_db()
        assert place.address

    def test_retry_policy(self):
        assert geocode_place.name == 'places.tasks.geocode_place'
        assert geocoding.GeocodingError in tuple(getattr(geocode_place, 'autoretry_for', ()))
        assert geocode_place.max_retries == 5
        assert geocode_place.retry_backoff


@pytest.mark.django_db
class TestServiceSchedulesTask:
    """Passo 4: add_place_to_board accoda il task con transaction.on_commit."""

    def test_task_queued_only_after_commit(self, board, monkeypatch, django_capture_on_commit_callbacks):
        queued = []
        monkeypatch.setattr(tasks.geocode_place, 'delay', lambda *args: queued.append(args))
        with django_capture_on_commit_callbacks() as callbacks:
            place = add_place_to_board(board, 'Colosseo', 41.8902, 12.4922)
        assert len(callbacks) == 1, 'una sola callback on_commit'
        assert queued == [], 'prima del commit il task non parte'
        callbacks[0]()
        assert queued == [(str(place.id),)], "al task si passa l'id come stringa, non l'oggetto"

    def test_address_after_commit(self, board, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks(execute=True):
            place = add_place_to_board(board, 'Pantheon', 41.8986, 12.4769)
            assert Place.objects.get(pk=place.pk).address == ''
        place.refresh_from_db()
        assert place.address == 'Indirizzo simulato (41.8986, 12.4769)'

    def test_invalid_place_queues_nothing(self, board, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks() as callbacks:
            with pytest.raises(ValueError):
                add_place_to_board(board, 'Fuori scala', 95, 0)
        assert callbacks == []
        with django_capture_on_commit_callbacks() as callbacks:
            add_place_to_board(board, 'Colosseo', 41.8902, 12.4922)
        assert len(callbacks) == 1

    def test_api_create_geocodes_after_commit(self, owner, board, django_capture_on_commit_callbacks):
        client = APIClient()
        client.force_authenticate(owner)
        with django_capture_on_commit_callbacks(execute=True):
            response = client.post(f'/api/v1/boards/{board.id}/places/',
                                   {'name': 'Colosseo', 'lat': 41.8902, 'lng': 12.4922},
                                   format='json')
        assert response.status_code == 201
        assert Place.objects.get(pk=response.json()['id']).address.startswith('Indirizzo simulato')
