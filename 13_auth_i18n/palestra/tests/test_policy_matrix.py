"""Matrice delle policy: ogni ruolo per ogni azione, in un solo test parametrizzato."""
import pytest
from django.contrib.auth.models import AnonymousUser

from boards.policies import can_add_collaborator, can_edit_board, can_view_board

ACTIONS = {'view': can_view_board, 'edit': can_edit_board, 'add_collaborator': can_add_collaborator}
EXPECTED = {
    'owner': {'view': True, 'edit': True, 'add_collaborator': True},
    'collaborator': {'view': True, 'edit': False, 'add_collaborator': False},
    'stranger': {'view': False, 'edit': False, 'add_collaborator': False},
    'anonymous': {'view': False, 'edit': False, 'add_collaborator': False},
}
CASES = [(role, action, allowed) for role, row in EXPECTED.items() for action, allowed in row.items()]


@pytest.fixture
def user_for(owner, collaborator, stranger):
    people = {'owner': owner, 'collaborator': collaborator, 'stranger': stranger,
              'anonymous': AnonymousUser()}
    return people.__getitem__


@pytest.mark.parametrize('role, action, allowed', CASES, ids=[f'{r}-{a}' for r, a, _ in CASES])
def test_policy(role, action, allowed, board, user_for):
    assert ACTIONS[action](user_for(role), board) is allowed