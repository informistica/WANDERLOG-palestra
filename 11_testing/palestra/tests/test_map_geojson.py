"""Livello 07: i luoghi di una bacheca in GeoJSON per l'isola della mappa."""
import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from boards.models import Board, Collaborator
from places.models import Place
from places.services import board_geojson, place_to_feature

User = get_user_model()


def map_url(board_id):
    return f'/api/v1/boards/{board_id}/map/'


def api(user=None):
    client = APIClient()
    if user is not None:
        client.force_authenticate(user)
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
    board = Board.objects.create(title='Roma', description='Tre giorni', owner=owner)
    Collaborator.objects.create(board=board, user=viewer)
    return board


@pytest.fixture
def places(board):
    colosseo = Place.objects.create(board=board, name='Colosseo', lat=41.8902, lng=12.4922,
                                    description='Anfiteatro Flavio')
    pantheon = Place.objects.create(board=board, name='Pantheon', lat=41.8986, lng=12.4769)
    return colosseo, pantheon


@pytest.mark.django_db
class TestPlaceGeojsonService:
    """Passo 1: i servizi che trasformano i luoghi in GeoJSON."""

    def test_place_to_feature(self, places):
        colosseo, _ = places
        assert place_to_feature(colosseo) == {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [12.4922, 41.8902]},
            'properties': {'id': str(colosseo.id), 'name': 'Colosseo',
                           'description': 'Anfiteatro Flavio'},
        }

    def test_board_geojson_empty_board(self, board):
        assert board_geojson(board) == {'type': 'FeatureCollection', 'features': []}

    def test_board_geojson_only_this_board(self, owner, board, places):
        other = Board.objects.create(title='Parigi', owner=owner)
        Place.objects.create(board=other, name='Louvre', lat=48.8606, lng=2.3376)
        names = [f['properties']['name'] for f in board_geojson(board)['features']]
        assert names == ['Colosseo', 'Pantheon']


@pytest.mark.django_db
class TestBoardMapApi:
    """Passo 2: GET /api/v1/boards/{id}/map/ con le regole del resto dell'API."""

    def test_login_required(self, owner, board):
        # Le due richieste insieme: il 403 da solo lo darebbe gia' DRF, anche senza view.
        assert api().get(map_url(board.id)).status_code == 403
        assert api(owner).get(map_url(board.id)).status_code == 200

    def test_feature_collection(self, owner, board, places):
        response = api(owner).get(map_url(board.id))
        assert response.status_code == 200
        assert response['Content-Type'].startswith('application/json')
        data = response.json()
        assert data['type'] == 'FeatureCollection'
        assert len(data['features']) == 2
        for feature in data['features']:
            assert feature['type'] == 'Feature'
            assert feature['geometry']['type'] == 'Point'

    def test_coordinates_are_lng_lat_numbers(self, owner, board, places):
        feature = api(owner).get(map_url(board.id)).json()['features'][0]
        coordinates = feature['geometry']['coordinates']
        assert coordinates == [12.4922, 41.8902]
        assert all(isinstance(c, float) for c in coordinates)

    def test_properties(self, owner, board, places):
        colosseo, pantheon = places
        features = api(owner).get(map_url(board.id)).json()['features']
        assert [f['properties'] for f in features] == [
            {'id': str(colosseo.id), 'name': 'Colosseo', 'description': 'Anfiteatro Flavio'},
            {'id': str(pantheon.id), 'name': 'Pantheon', 'description': ''},
        ]

    def test_only_places_of_this_board(self, owner, board, places):
        other = Board.objects.create(title='Parigi', owner=owner)
        Place.objects.create(board=other, name='Louvre', lat=48.8606, lng=2.3376)
        features = api(owner).get(map_url(board.id)).json()['features']
        assert [f['properties']['name'] for f in features] == ['Colosseo', 'Pantheon']

    def test_empty_board(self, owner, board):
        response = api(owner).get(map_url(board.id))
        assert response.status_code == 200
        assert response.json() == {'type': 'FeatureCollection', 'features': []}

    def test_collaborator_can_view(self, viewer, board, places):
        response = api(viewer).get(map_url(board.id))
        assert response.status_code == 200
        assert len(response.json()['features']) == 2

    def test_stranger_gets_404(self, stranger, board, places):
        response = api(stranger).get(map_url(board.id))
        assert response.status_code == 404
        assert response['Content-Type'].startswith('application/json')

    def test_unknown_board_404(self, owner):
        response = api(owner).get(map_url(uuid.uuid4()))
        assert response.status_code == 404
        assert response['Content-Type'].startswith('application/json')
