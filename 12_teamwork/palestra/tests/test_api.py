"""Livello 05: configurazione DRF, autenticazione, bacheche e collaboratori via API."""
import uuid

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIClient

from boards.models import Board, Collaborator

User = get_user_model()
API = '/api/v1'


def assert_status(response, expected):
    assert response.status_code == expected
    if expected == 404:
        # deve essere un 404 dell'API (JSON di DRF), non la pagina di Django per un URL inesistente
        assert response['Content-Type'].startswith('application/json')


def client_for(user=None):
    client = APIClient()
    if user is not None:
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


class TestConfigurazione:
    """Passo 1: DRF installato e configurato come in WANDERLOG."""

    def test_rest_framework_installed(self):
        assert 'rest_framework' in settings.INSTALLED_APPS

    def test_session_authentication(self):
        conf = getattr(settings, 'REST_FRAMEWORK', {})
        assert conf.get('DEFAULT_AUTHENTICATION_CLASSES') == [
            'rest_framework.authentication.SessionAuthentication']

    def test_default_permission_is_authenticated(self):
        conf = getattr(settings, 'REST_FRAMEWORK', {})
        assert conf.get('DEFAULT_PERMISSION_CLASSES') == [
            'rest_framework.permissions.IsAuthenticated']

    def test_default_pagination(self):
        conf = getattr(settings, 'REST_FRAMEWORK', {})
        assert conf.get('DEFAULT_PAGINATION_CLASS') == 'core.pagination.DefaultPagination'
        assert conf.get('PAGE_SIZE') == 20

    def test_pagination_class(self):
        from core.pagination import DefaultPagination
        assert DefaultPagination.page_size == 20
        assert DefaultPagination.page_size_query_param == 'page_size'
        assert DefaultPagination.max_page_size == 100


@pytest.mark.django_db
class TestBoardsVisibleTo:
    """Passo 2: servizio di lettura boards_visible_to."""

    def test_owner_and_collaborator_see_board(self, board, owner, viewer):
        from boards.services import boards_visible_to
        assert list(boards_visible_to(owner)) == [board]
        assert list(boards_visible_to(viewer)) == [board]

    def test_stranger_sees_nothing(self, board, stranger):
        from boards.services import boards_visible_to
        assert list(boards_visible_to(stranger)) == []

    def test_anonymous_and_none_see_nothing(self, board):
        from boards.services import boards_visible_to
        assert list(boards_visible_to(AnonymousUser())) == []
        assert list(boards_visible_to(None)) == []

    def test_no_duplicates_with_many_collaborators(self, board, owner, stranger):
        from boards.services import boards_visible_to
        Collaborator.objects.create(board=board, user=stranger)
        assert list(boards_visible_to(owner)) == [board]


@pytest.mark.django_db
class TestAutenticazione:
    """Passi 1 e 7: le route esistono e richiedono il login."""

    @pytest.mark.parametrize('path', ['/boards/', '/boards/{id}/', '/boards/{id}/places/'])
    def test_anonymous_is_rejected(self, board, path):
        response = client_for().get(API + path.format(id=board.id))
        assert response.status_code in (401, 403)

    def test_anonymous_cannot_create(self, db):
        response = client_for().post(f'{API}/boards/', {'title': 'X'}, format='json')
        assert response.status_code in (401, 403)
        assert Board.objects.count() == 0


@pytest.mark.django_db
class TestBoardsApi:
    """Passi 3-5 e 7: /api/v1/boards/."""

    def test_list_only_visible_boards(self, board, owner, viewer, stranger):
        Board.objects.create(title='Parigi', owner=stranger)
        for user in (owner, viewer):
            response = client_for(user).get(f'{API}/boards/')
            assert response.status_code == 200
            assert [b['title'] for b in response.data['results']] == ['Roma']
        response = client_for(stranger).get(f'{API}/boards/')
        assert [b['title'] for b in response.data['results']] == ['Parigi']

    def test_list_without_duplicates(self, board, owner, stranger):
        Collaborator.objects.create(board=board, user=stranger)
        response = client_for(owner).get(f'{API}/boards/')
        assert response.data['count'] == 1

    def test_list_is_paginated(self, owner):
        for i in range(25):
            Board.objects.create(title=f'B{i}', owner=owner)
        response = client_for(owner).get(f'{API}/boards/')
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20
        assert response.data['next'] is not None

    def test_board_fields(self, board, owner):
        response = client_for(owner).get(f'{API}/boards/{board.id}/')
        assert response.status_code == 200
        assert set(response.data) == {'id', 'title', 'description', 'owner',
                                      'created_at', 'updated_at'}
        assert response.data['owner'] == 'owner@example.com'

    def test_create_uses_service(self, owner):
        response = client_for(owner).post(
            f'{API}/boards/', {'title': '  Milano  ', 'description': 'Weekend'}, format='json')
        assert response.status_code == 201
        assert response.data['title'] == 'Milano'
        assert response.data['owner'] == 'owner@example.com'
        assert Board.objects.get(pk=response.data['id']).owner == owner

    def test_owner_cannot_be_forced(self, owner, stranger):
        response = client_for(owner).post(
            f'{API}/boards/', {'title': 'Napoli', 'owner': stranger.email}, format='json')
        assert response.status_code == 201
        assert Board.objects.get(pk=response.data['id']).owner == owner

    def test_create_empty_title_is_400(self, owner):
        response = client_for(owner).post(f'{API}/boards/', {'title': '   '}, format='json')
        assert response.status_code == 400
        assert Board.objects.count() == 0

    def test_retrieve_matrix(self, board, owner, viewer, stranger):
        url = f'{API}/boards/{board.id}/'
        assert client_for(owner).get(url).status_code == 200
        assert client_for(viewer).get(url).status_code == 200
        # chi non può vedere non scopre nemmeno che la bacheca esiste
        assert_status(client_for(stranger).get(url), 404)

    def test_retrieve_unknown_board_is_404(self, owner):
        assert_status(client_for(owner).get(f'{API}/boards/{uuid.uuid4()}/'), 404)

    @pytest.mark.parametrize('user_fixture,expected', [
        ('owner', 200), ('viewer', 403), ('stranger', 404)])
    def test_update_matrix(self, request, board, user_fixture, expected):
        user = request.getfixturevalue(user_fixture)
        response = client_for(user).patch(
            f'{API}/boards/{board.id}/', {'title': 'Roma 2026'}, format='json')
        assert_status(response, expected)
        board.refresh_from_db()
        assert (board.title == 'Roma 2026') == (expected == 200)

    @pytest.mark.parametrize('user_fixture,expected', [
        ('owner', 204), ('viewer', 403), ('stranger', 404)])
    def test_delete_matrix(self, request, board, user_fixture, expected):
        user = request.getfixturevalue(user_fixture)
        response = client_for(user).delete(f'{API}/boards/{board.id}/')
        assert_status(response, expected)
        assert Board.objects.filter(pk=board.pk).exists() == (expected != 204)


@pytest.mark.django_db
class TestCollaboratorsApi:
    """Passi 4-5: POST /api/v1/boards/{id}/collaborators/ passa da add_collaborator."""

    def url(self, board):
        return f'{API}/boards/{board.id}/collaborators/'

    def test_owner_adds_collaborator(self, board, owner, stranger):
        response = client_for(owner).post(self.url(board), {'user': stranger.email}, format='json')
        assert response.status_code == 201
        assert response.data['user'] == 'stranger@example.com'
        assert response.data['role'] == 'viewer'
        assert board.collaborators.filter(user=stranger).exists()

    def test_collaborator_cannot_add(self, board, viewer, stranger):
        response = client_for(viewer).post(self.url(board), {'user': stranger.email}, format='json')
        assert response.status_code == 403
        assert not board.collaborators.filter(user=stranger).exists()

    def test_stranger_gets_404(self, board, stranger):
        response = client_for(stranger).post(self.url(board), {'user': stranger.email},
                                             format='json')
        assert_status(response, 404)

    @pytest.mark.parametrize('email', ['viewer@example.com', 'owner@example.com',
                                       'nessuno@example.com'])
    def test_invalid_collaborator_is_400(self, board, owner, email):
        response = client_for(owner).post(self.url(board), {'user': email}, format='json')
        assert response.status_code == 400
        assert board.collaborators.count() == 1
