"""Livello 07: la pagina della mappa con l'isola JavaScript di Leaflet."""
import re
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders

from boards.models import Board, Collaborator
from places.models import Place

User = get_user_model()


def map_page(board_id):
    return f'/boards/{board_id}/mappa/'


def opening_tag(html, element_id):
    """Il tag di apertura dell'elemento con quell'id (stringa vuota se manca)."""
    match = re.search(r'<[a-z]+[^>]*\bid="%s"[^>]*>' % re.escape(element_id), html)
    return match.group(0) if match else ''


def login(client, user):
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
    board = Board.objects.create(title='Roma', description='Tre giorni', owner=owner)
    Collaborator.objects.create(board=board, user=viewer)
    return board


@pytest.fixture
def place(board):
    return Place.objects.create(board=board, name='Colosseo', lat=41.8902, lng=12.4922)


@pytest.mark.django_db
class TestMapPage:
    """Passi 3-4: la pagina /boards/{id}/mappa/."""

    def test_anonymous_redirected_to_login(self, client, board):
        response = client.get(map_page(board.id))
        assert response.status_code == 302
        assert response['Location'] == f'/accounts/login/?next=/boards/{board.id}/mappa/'

    def test_owner_sees_map_container(self, client, owner, board):
        response = login(client, owner).get(map_page(board.id))
        assert response.status_code == 200
        names = [t.name for t in response.templates]
        assert 'places/board_map.html' in names and 'base.html' in names
        tag = opening_tag(response.content.decode(), 'board-map')
        assert f'data-geojson-url="/api/v1/boards/{board.id}/map/"' in tag
        assert 'aria-label="' in tag

    def test_detail_page_links_to_map(self, client, owner, board):
        login(client, owner)
        assert client.get(map_page(board.id)).status_code == 200
        html = client.get(f'/boards/{board.id}/').content.decode()
        assert f'href="/boards/{board.id}/mappa/"' in html

    def test_collaborator_sees_map(self, client, viewer, board):
        assert login(client, viewer).get(map_page(board.id)).status_code == 200

    def test_stranger_gets_404(self, client, stranger, owner, board):
        assert login(client, owner).get(map_page(board.id)).status_code == 200
        assert login(client, stranger).get(map_page(board.id)).status_code == 404

    def test_unknown_board_404(self, client, owner, board):
        login(client, owner)
        assert client.get(map_page(board.id)).status_code == 200
        assert client.get(map_page(uuid.uuid4())).status_code == 404

    def test_leaflet_only_on_map_page(self, client, owner, board):
        login(client, owner)
        html = client.get(map_page(board.id)).content.decode()
        head = html.split('</head>')[0]
        assert 'href="/static/places/leaflet/leaflet.css"' in head
        leaflet = html.find('src="/static/places/leaflet/leaflet.js"')
        island = html.find('src="/static/places/map.js"')
        assert 0 < leaflet < island, 'prima Leaflet, poi map.js'
        assert 'unpkg.com' not in html and 'cdn' not in html.lower()
        for other in ('/boards/', f'/boards/{board.id}/'):
            assert 'leaflet' not in client.get(other).content.decode().lower()

    def test_empty_board_message(self, client, owner, board):
        html = login(client, owner).get(map_page(board.id)).content.decode()
        tag = opening_tag(html, 'mappa-vuota')
        assert tag and 'hidden' not in tag

    def test_empty_message_hidden_with_places(self, client, owner, board, place):
        html = login(client, owner).get(map_page(board.id)).content.decode()
        assert 'hidden' in opening_tag(html, 'mappa-vuota')


class TestStaticFiles:
    """Passo 5: Leaflet vendorizzato e l'isola map.js."""

    def test_leaflet_vendored_and_island_written(self):
        leaflet_js = finders.find('places/leaflet/leaflet.js')
        assert leaflet_js, 'Leaflet deve stare tra i file statici, non su un CDN'
        assert 'Leaflet 1.9.4' in open(leaflet_js, encoding='utf-8').read(500)
        assert finders.find('places/leaflet/leaflet.css')
        assert finders.find('places/leaflet/images/marker-icon.png')
        island = finders.find('places/map.js')
        assert island
        js = open(island, encoding='utf-8').read()
        for pattern in (r'L\.map\(', r'fetch\(', r'dataset\.geojsonUrl',
                        r'L\.geoJSON\(', r'\.bindPopup\(', r'\.fitBounds\(',
                        r'\.textContent\s*='):
            assert re.search(pattern, js), pattern
        assert 'innerHTML' not in js
