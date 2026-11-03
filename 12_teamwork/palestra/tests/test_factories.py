"""Livello 11 (bersaglio): le factory di tests/factories.py."""
import pytest

from boards.models import Board, Collaborator, User
from boards.policies import can_edit_board, can_view_board
from inbox.models import InboundAddress
from places.models import Place
from tests import factories as f

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('name, model', [
    ('UserFactory', User), ('BoardFactory', Board), ('CollaboratorFactory', Collaborator),
    ('PlaceFactory', Place), ('InboundAddressFactory', InboundAddress),
])
def test_is_django_model_factory(name, model):
    from factory.django import DjangoModelFactory
    cls = getattr(f, name)
    assert issubclass(cls, DjangoModelFactory), f'{name} deve estendere DjangoModelFactory'
    assert cls._meta.model is model


def test_user_emails_are_unique():
    users = f.UserFactory.create_batch(3)
    assert len({u.email for u in users}) == 3
    assert User.objects.count() == 3


def test_user_password_is_hashed():
    user = User.objects.get(pk=f.UserFactory().pk)
    assert user.check_password('password')
    assert user.password != 'password'


def test_build_does_not_touch_the_database():
    user = f.UserFactory.build()
    assert isinstance(user, User)
    assert User.objects.count() == 0


def test_board_creates_its_owner():
    board = f.BoardFactory()
    assert board.title
    assert isinstance(board.owner, User) and board.owner.pk
    assert can_edit_board(board.owner, board)


def test_board_owner_can_be_overridden():
    owner = f.UserFactory(email='anna@example.com')
    board = f.BoardFactory(owner=owner)
    assert board.owner == owner
    assert User.objects.count() == 1


def test_board_with_places():
    board = f.BoardFactory(with_places=3)
    assert board.places.count() == 3
    assert f.BoardFactory().places.count() == 0


def test_collaborator_can_view_not_edit():
    c = f.CollaboratorFactory()
    assert c.user != c.board.owner
    assert c.role == Collaborator.ROLE_VIEWER
    assert can_view_board(c.user, c.board)
    assert not can_edit_board(c.user, c.board)


def test_place_coordinates_are_valid():
    for place in f.PlaceFactory.create_batch(5):
        assert place.name
        assert -90 <= place.lat <= 90 and -180 <= place.lng <= 180
        assert place.board.pk


def test_inbound_address():
    address = f.InboundAddressFactory()
    assert len(address.token) == 16
    assert address.board.inbound_address == address