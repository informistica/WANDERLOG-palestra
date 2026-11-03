"""Livello 05: luoghi di una bacheca via API (/api/v1/boards/{board_pk}/places/)."""
import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from boards.models import Board, Collaborator
from places.models import Place

User = get_user_model()
API = '/api/v1'


def assert_status(response, expected):
    assert response.status_code == expected
    if expected == 404:
        # deve essere un 404 dell'API (JSON di DRF), non la pagina di Django per un URL inesistente
        assert response['Content-Type'].startswith('application/json')


def client_for(user):
    client = APIClient()
    client.force_login(user)
    return client


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@example.com', password='test12345')


@pytest.fixture
def viewer(db):
    return User.objects.create_user(email='viewer@example.com', password='test12345')


@pytest.fixture
def stranger(db):
    return User.objects.create_user(email='stranger@example.com', password='test12345')


@pytest.fixture
def board(owner, viewer):
    board = Board.objects.create(title='Roma', owner=owner)
    Collaborator.objects.create(board=board, user=viewer)
    return board


@pytest.fixture
def place(board):
    return Place.objects.create(board=board, name='Colosseo', lat=41.8902, lng=12.4922)


def places_url(board_id):
    return f'{API}/boards/{board_id}/places/'


@pytest.mark.django_db
class TestPlacesRead:
    """Passi 4, 6 e 7: lettura."""

    @pytest.mark.parametrize('user_fixture', ['owner', 'viewer'])
    def test_list(self, request, board, place, user_fixture):
        user = request.getfixturevalue(user_fixture)
        response = client_for(user).get(places_url(board.id))
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Colosseo'

    def test_list_only_this_board(self, board, place, owner):
        other = Board.objects.create(title='Parigi', owner=owner)
        Place.objects.create(board=other, name='Louvre', lat=48.86, lng=2.33)
        response = client_for(owner).get(places_url(board.id))
        assert [p['name'] for p in response.data['results']] == ['Colosseo']

    def test_place_fields(self, board, place, owner):
        response = client_for(owner).get(f'{places_url(board.id)}{place.id}/')
        assert response.status_code == 200
        assert set(response.data) == {'id', 'board', 'name', 'description', 'lat', 'lng',
                                      'created_at'}
        assert str(response.data['board']) == str(board.id)

    def test_stranger_gets_404(self, board, place, stranger):
        assert_status(client_for(stranger).get(places_url(board.id)), 404)
        assert_status(client_for(stranger).get(
            f'{places_url(board.id)}{place.id}/'), 404)

    @pytest.mark.parametrize('board_id', [uuid.uuid4(), 'non-un-uuid'])
    def test_unknown_board_is_404(self, owner, board_id):
        assert_status(client_for(owner).get(places_url(board_id)), 404)

    def test_place_of_other_board_is_404(self, board, owner):
        other = Board.objects.create(title='Parigi', owner=owner)
        louvre = Place.objects.create(board=other, name='Louvre', lat=48.86, lng=2.33)
        response = client_for(owner).get(f'{places_url(board.id)}{louvre.id}/')
        assert_status(response, 404)


@pytest.mark.django_db
class TestPlacesWrite:
    """Passi 4, 6 e 7: scrittura tramite add_place_to_board e policy della bacheca."""

    payload = {'name': 'Pantheon', 'lat': 41.8986, 'lng': 12.4769, 'description': 'Cupola'}

    def test_owner_creates_place(self, board, owner):
        response = client_for(owner).post(places_url(board.id), self.payload, format='json')
        assert response.status_code == 201
        assert str(response.data['board']) == str(board.id)
        assert board.places.get().name == 'Pantheon'

    def test_board_comes_from_url(self, board, owner):
        other = Board.objects.create(title='Parigi', owner=owner)
        data = dict(self.payload, board=str(other.id))
        response = client_for(owner).post(places_url(board.id), data, format='json')
        assert response.status_code == 201
        assert other.places.count() == 0
        assert board.places.count() == 1

    @pytest.mark.parametrize('lat,lng', [(91, 0), (0, 181), (-90.5, 0)])
    def test_invalid_coordinates_are_400(self, board, owner, lat, lng):
        data = dict(self.payload, lat=lat, lng=lng)
        response = client_for(owner).post(places_url(board.id), data, format='json')
        assert response.status_code == 400
        assert board.places.count() == 0

    def test_viewer_cannot_create(self, board, viewer):
        response = client_for(viewer).post(places_url(board.id), self.payload, format='json')
        assert response.status_code == 403
        assert board.places.count() == 0

    def test_stranger_cannot_create(self, board, stranger):
        response = client_for(stranger).post(places_url(board.id), self.payload, format='json')
        assert_status(response, 404)
        assert board.places.count() == 0

    @pytest.mark.parametrize('user_fixture,expected', [
        ('owner', 204), ('viewer', 403), ('stranger', 404)])
    def test_delete_matrix(self, request, board, place, user_fixture, expected):
        user = request.getfixturevalue(user_fixture)
        response = client_for(user).delete(f'{places_url(board.id)}{place.id}/')
        assert_status(response, expected)
        assert Place.objects.filter(pk=place.pk).exists() == (expected != 204)
