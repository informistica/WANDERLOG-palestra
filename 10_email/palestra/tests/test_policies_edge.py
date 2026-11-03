"""Casi limite delle policy e admin di Collaborator (passi 2-4)."""
import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from boards.models import Board, Collaborator
from boards.policies import can_add_collaborator, can_edit_board, can_view_board
from boards.services import add_collaborator

User = get_user_model()


@pytest.fixture
def board(db):
    owner = User.objects.create_user(email='owner@example.com', password='test12345')
    return Board.objects.create(title='Roma', owner=owner)


@pytest.mark.parametrize('anon', [None, AnonymousUser()])
@pytest.mark.parametrize('policy', [can_view_board, can_edit_board, can_add_collaborator])
def test_anonymous_can_do_nothing(board, anon, policy):
    assert policy(anon, board) is False


def test_cannot_add_same_collaborator_twice(board):
    viewer = User.objects.create_user(email='viewer@example.com', password='test12345')
    add_collaborator(board, viewer, requesting_user=board.owner)
    with pytest.raises(ValueError):
        add_collaborator(board, viewer, requesting_user=board.owner)
    assert Collaborator.objects.count() == 1


def test_anonymous_cannot_add_collaborator(board):
    viewer = User.objects.create_user(email='viewer@example.com', password='test12345')
    with pytest.raises(PermissionError):
        add_collaborator(board, viewer, requesting_user=AnonymousUser())


def test_collaborator_registered_in_admin():
    assert Collaborator in admin.site._registry
