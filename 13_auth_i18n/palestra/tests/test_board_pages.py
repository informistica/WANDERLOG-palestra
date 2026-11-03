"""Livello 06: pagine delle bacheche con template Django e partial HTMX."""
import re
import uuid

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from boards.models import Board, Collaborator
from places.models import Place

User = get_user_model()
HX = {'HX-Request': 'true'}


def template_names(response):
    return [t.name for t in response.templates]


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


@pytest.mark.django_db
class TestLoginRequired:
    """Passo 6-7: tutte le pagine richiedono il login."""

    @pytest.mark.parametrize('method,path', [
        ('get', '/boards/'),
        ('post', '/boards/nuova/'),
        ('get', '/boards/{id}/'),
        ('post', '/boards/{id}/modifica/'),
    ])
    def test_anonymous_redirected_to_login(self, client, board, method, path):
        url = path.format(id=board.id)
        if method == 'get':
            response = client.get(url)
        else:
            response = client.post(url, {'title': 'Intruso'})
        assert response.status_code == 302
        assert response['Location'] == f'/accounts/login/?next={url}'
        board.refresh_from_db()
        assert board.title == 'Roma'
        assert Board.objects.count() == 1


@pytest.mark.django_db
class TestBoardList:
    """Passo 5-6: lista completa o partial a seconda dell'header HX-Request."""

    def test_full_page(self, client, owner, board, stranger):
        Board.objects.create(title='Parigi', owner=stranger)
        response = login(client, owner).get('/boards/')
        assert response.status_code == 200
        assert 'boards/board_list.html' in template_names(response)
        html = response.content.decode()
        assert f'href="/boards/{board.id}/"' in html
        assert 'Roma' in html and 'Parigi' not in html

    def test_viewer_sees_shared_board(self, client, viewer, board):
        html = login(client, viewer).get('/boards/').content.decode()
        assert 'Roma' in html and 'owner@example.com' in html

    def test_htmx_returns_only_partial(self, client, owner, board):
        response = login(client, owner).get('/boards/', headers=HX)
        assert response.status_code == 200
        names = template_names(response)
        assert 'boards/_board_list.html' in names and 'base.html' not in names
        html = response.content.decode()
        assert '<html' not in html
        assert opening_tag(html, 'board-list').startswith('<ul')
        assert 'Roma' in html

    def test_empty_message(self, client, stranger):
        html = login(client, stranger).get('/boards/').content.decode()
        assert 'Nessuna bacheca, per ora.' in html

    def test_create_form_uses_hx_post(self, client, owner):
        html = login(client, owner).get('/boards/').content.decode()
        tag = opening_tag(html, 'board-form')
        assert tag.startswith('<form')
        assert 'method="post"' in tag and 'action="/boards/nuova/"' in tag
        assert 'hx-post="/boards/nuova/"' in tag
        assert 'hx-target="#board-list"' in tag and 'hx-swap="outerHTML"' in tag
        assert 'name="title"' in html and 'name="description"' in html


@pytest.mark.django_db
class TestBoardCreate:
    """Passo 4-6: creazione con hx-post che restituisce il partial della lista."""

    def test_htmx_valid_returns_list_partial(self, client, owner, board):
        response = login(client, owner).post(
            '/boards/nuova/', {'title': '  Milano  ', 'description': 'Weekend'}, headers=HX)
        assert response.status_code == 200
        names = template_names(response)
        assert 'boards/_board_list.html' in names and 'base.html' not in names
        html = response.content.decode()
        assert 'Milano' in html and 'Roma' in html
        created = Board.objects.get(title='Milano')
        assert created.owner == owner and created.description == 'Weekend'

    def test_htmx_invalid_retargets_form(self, client, owner):
        response = login(client, owner).post('/boards/nuova/', {'title': ''}, headers=HX)
        assert response.status_code == 200
        assert response['HX-Retarget'] == '#board-form'
        assert response['HX-Reswap'] == 'outerHTML'
        assert 'boards/_board_form.html' in template_names(response)
        assert opening_tag(response.content.decode(), 'board-form').startswith('<form')
        assert Board.objects.count() == 0

    def test_htmx_blank_title_is_rejected(self, client, owner):
        response = login(client, owner).post('/boards/nuova/', {'title': '   '}, headers=HX)
        assert response['HX-Retarget'] == '#board-form'
        assert Board.objects.count() == 0

    def test_without_htmx_redirects(self, client, owner):
        response = login(client, owner).post('/boards/nuova/', {'title': 'Napoli'})
        assert response.status_code == 302
        assert response['Location'] == '/boards/'
        assert Board.objects.filter(title='Napoli', owner=owner).exists()

    def test_without_htmx_invalid_shows_full_page(self, client, owner):
        response = login(client, owner).post('/boards/nuova/', {'title': ''})
        assert response.status_code == 200
        assert 'boards/board_list.html' in template_names(response)
        assert response.context['form'].errors
        assert Board.objects.count() == 0

    def test_get_not_allowed(self, client, owner):
        assert login(client, owner).get('/boards/nuova/').status_code == 405


@pytest.mark.django_db
class TestBoardDetail:
    """Passo 7: dettaglio con le policy: estraneo 404, lettore senza modifica."""

    def test_owner_sees_board_and_edit_form(self, client, owner, board):
        Place.objects.create(board=board, name='Colosseo', lat=41.89, lng=12.49)
        response = login(client, owner).get(f'/boards/{board.id}/')
        assert response.status_code == 200
        assert 'boards/board_detail.html' in template_names(response)
        html = response.content.decode()
        assert opening_tag(html, 'board-header')
        assert 'Roma' in html and 'Tre giorni' in html and 'Colosseo' in html
        tag = opening_tag(html, 'board-edit-form')
        assert f'hx-post="/boards/{board.id}/modifica/"' in tag
        assert 'hx-target="#board-header"' in tag
        assert response.context['can_edit'] is True

    def test_edit_form_prefilled(self, client, owner, board):
        html = login(client, owner).get(f'/boards/{board.id}/').content.decode()
        assert re.search(r'<input[^>]*name="title"[^>]*value="Roma"', html)

    def test_viewer_sees_board_without_edit_form(self, client, viewer, board):
        response = login(client, viewer).get(f'/boards/{board.id}/')
        assert response.status_code == 200
        html = response.content.decode()
        assert 'Roma' in html
        assert 'board-edit-form' not in html
        assert response.context['can_edit'] is False

    def test_stranger_gets_404(self, client, stranger, board):
        response = login(client, stranger).get(f'/boards/{board.id}/')
        assert response.status_code == 404

    def test_unknown_board_404(self, client, owner):
        response = login(client, owner).get(f'/boards/{uuid.uuid4()}/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestBoardEdit:
    """Passo 7: modifica con hx-post che restituisce il partial dell'intestazione."""

    def test_owner_htmx_returns_header_partial(self, client, owner, board):
        response = login(client, owner).post(
            f'/boards/{board.id}/modifica/', {'title': ' Roma 2026 ', 'description': 'Nuova'},
            headers=HX)
        assert response.status_code == 200
        names = template_names(response)
        assert 'boards/_board_header.html' in names and 'base.html' not in names
        html = response.content.decode()
        assert opening_tag(html, 'board-header') and 'Roma 2026' in html
        board.refresh_from_db()
        assert (board.title, board.description) == ('Roma 2026', 'Nuova')

    def test_owner_without_htmx_redirects(self, client, owner, board):
        response = login(client, owner).post(f'/boards/{board.id}/modifica/', {'title': 'Roma 2'})
        assert response.status_code == 302
        assert response['Location'] == f'/boards/{board.id}/'
        board.refresh_from_db()
        assert board.title == 'Roma 2'

    def test_owner_invalid_retargets_form(self, client, owner, board):
        response = login(client, owner).post(
            f'/boards/{board.id}/modifica/', {'title': ''}, headers=HX)
        assert response.status_code == 200
        assert response['HX-Retarget'] == '#board-edit-form'
        assert response['HX-Reswap'] == 'outerHTML'
        assert 'boards/_board_edit_form.html' in template_names(response)
        board.refresh_from_db()
        assert board.title == 'Roma'

    @pytest.mark.parametrize('headers', [{}, HX])
    def test_viewer_forbidden(self, client, viewer, board, headers):
        response = login(client, viewer).post(
            f'/boards/{board.id}/modifica/', {'title': 'Mia'}, headers=headers)
        assert response.status_code == 403
        board.refresh_from_db()
        assert board.title == 'Roma'

    def test_viewer_forbidden_even_with_invalid_data(self, client, viewer, board):
        response = login(client, viewer).post(f'/boards/{board.id}/modifica/', {'title': ''},
                                              headers=HX)
        assert response.status_code == 403

    def test_stranger_gets_404(self, client, stranger, board):
        response = login(client, stranger).post(f'/boards/{board.id}/modifica/', {'title': 'Mia'})
        assert response.status_code == 404
        board.refresh_from_db()
        assert board.title == 'Roma'

    def test_get_not_allowed(self, client, owner, board):
        assert login(client, owner).get(f'/boards/{board.id}/modifica/').status_code == 405


@pytest.mark.django_db
class TestUpdateBoardService:
    """Passo 4: update_board riusa la policy can_edit_board."""

    def test_owner_updates(self, owner, board):
        from boards.services import update_board
        update_board(board, '  Roma bis ', 'Altro', requesting_user=owner)
        board.refresh_from_db()
        assert (board.title, board.description) == ('Roma bis', 'Altro')

    @pytest.mark.parametrize('who', ['viewer', 'stranger', 'anonymous'])
    def test_others_cannot_update(self, request, board, who):
        from boards.services import update_board
        user = AnonymousUser() if who == 'anonymous' else request.getfixturevalue(who)
        with pytest.raises(PermissionError):
            update_board(board, 'Mia', requesting_user=user)
        board.refresh_from_db()
        assert board.title == 'Roma'

    def test_empty_title_rejected(self, owner, board):
        from boards.services import update_board
        with pytest.raises(ValueError):
            update_board(board, '   ', requesting_user=owner)
        board.refresh_from_db()
        assert board.title == 'Roma'
