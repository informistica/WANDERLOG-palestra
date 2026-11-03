"""Livello 11 (bersaglio): le fixture di tests/conftest.py."""
import pytest
from django.urls import reverse

from boards.models import Collaborator
from boards.policies import can_edit_board, can_view_board

pytestmark = pytest.mark.django_db


def test_owner_and_stranger(owner, stranger):
    assert owner.email == 'owner@example.com'
    assert stranger.email == 'stranger@example.com'
    assert owner.pk and stranger.pk and owner != stranger


def test_board_belongs_to_owner(board, owner, stranger):
    assert board.title == 'Roma'
    assert board.owner == owner
    assert not can_view_board(stranger, board)


def test_collaborator_is_a_user_on_board(board, collaborator):
    assert collaborator.email == 'collaborator@example.com'
    assert Collaborator.objects.filter(board=board, user=collaborator).exists()
    assert can_view_board(collaborator, board) and not can_edit_board(collaborator, board)


def test_place(place, board):
    assert place.board == board
    assert (place.name, place.lat, place.lng) == ('Colosseo', 41.8902, 12.4922)


def test_owner_client_is_logged_in(owner_client, board):
    response = owner_client.get(reverse('boards:detail', args=[board.pk]))
    assert response.status_code == 200
    assert 'Roma' in response.content.decode()


def test_api_client_owner(api_client_owner, board):
    response = api_client_owner.get('/api/v1/boards/')
    assert response.status_code == 200
    assert str(board.pk) in response.content.decode()


def test_fixtures_are_isolated(owner):
    """Function scope: ogni test riparte da un database pulito."""
    from boards.models import Board, User
    assert User.objects.count() == 1
    assert Board.objects.count() == 0