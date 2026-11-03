"""Test del service layer (passi 1-2)."""
import pytest
from django.contrib.auth import get_user_model

from boards.models import Board
from boards.services import create_board
from places.models import Place
from places.services import add_place_to_board

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email='owner@example.com', password='test12345')


@pytest.fixture
def board(owner):
    return Board.objects.create(title='Roma', owner=owner)


def test_create_board(owner):
    board = create_board(owner, 'Luoghi preferiti', 'La mia bacheca')
    assert board.pk is not None
    assert Board.objects.get(pk=board.pk).owner == owner
    assert board.description == 'La mia bacheca'


def test_create_board_strips_title(owner):
    assert create_board(owner, '  Roma  ').title == 'Roma'


@pytest.mark.parametrize('title', ['', '   ', None])
def test_create_board_requires_title(owner, title):
    with pytest.raises(ValueError):
        create_board(owner, title)
    assert Board.objects.count() == 0


def test_add_place_to_board(board):
    place = add_place_to_board(board, 'Colosseo', 41.8902, 12.4922, 'Anfiteatro Flavio')
    assert place.pk is not None
    assert list(board.places.all()) == [place]
    assert place.lat == 41.8902 and place.lng == 12.4922


def test_add_place_requires_board(db):
    with pytest.raises(ValueError):
        add_place_to_board(None, 'Colosseo', 41.89, 12.49)


@pytest.mark.parametrize('lat,lng', [(91, 0), (-90.5, 0), (0, 180.1), (0, -181)])
def test_add_place_rejects_bad_coordinates(board, lat, lng):
    with pytest.raises(ValueError):
        add_place_to_board(board, 'Fuori mappa', lat, lng)
    assert Place.objects.count() == 0
