"""Livello 06: login, layout base, HTMX vendorizzato e token CSRF per HTMX."""
import re

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import Client, RequestFactory

from boards.models import Board

User = get_user_model()
HX = {'HX-Request': 'true'}


def template_names(response):
    return [t.name for t in response.templates]


@pytest.fixture
def user(db):
    return User.objects.create_user(email='owner@example.com', password='test12345')


@pytest.fixture
def logged(client, user):
    client.force_login(user)
    return client


class TestLogin:
    """Passo 1: login con django.contrib.auth e redirect configurati."""

    def test_login_settings(self):
        assert getattr(settings, 'LOGIN_URL', None) == 'login'
        assert getattr(settings, 'LOGIN_REDIRECT_URL', None) == 'boards:list'
        assert getattr(settings, 'LOGOUT_REDIRECT_URL', None) == 'login'

    def test_login_page_shows_form(self, client, db):
        response = client.get('/accounts/login/')
        assert response.status_code == 200
        html = response.content.decode()
        assert 'base.html' in template_names(response)
        assert 'name="username"' in html
        assert 'name="password"' in html
        assert 'name="csrfmiddlewaretoken"' in html

    def test_login_redirects_to_board_list(self, client, user):
        response = client.post('/accounts/login/',
                               {'username': 'owner@example.com', 'password': 'test12345'})
        assert response.status_code == 302
        assert response['Location'] == '/boards/'


class TestIsHtmx:
    """Passo 2: core.htmx.is_htmx riconosce le richieste HTMX dall'header HX-Request."""

    def test_true_with_header(self):
        from core.htmx import is_htmx
        assert is_htmx(RequestFactory().get('/', headers=HX)) is True

    def test_false_without_header(self):
        from core.htmx import is_htmx
        assert is_htmx(RequestFactory().get('/')) is False

    def test_false_with_other_value(self):
        from core.htmx import is_htmx
        assert is_htmx(RequestFactory().get('/', headers={'HX-Request': 'false'})) is False


@pytest.mark.django_db
class TestBaseTemplate:
    """Passo 3: base.html carica HTMX locale, manda il CSRF negli header, annuncia i cambi."""

    def test_full_page_uses_base(self, logged):
        response = logged.get('/boards/')
        assert response.status_code == 200
        assert 'base.html' in template_names(response)
        assert '<html' in response.content.decode()

    def test_htmx_is_vendored_static_file(self, logged):
        html = logged.get('/boards/').content.decode()
        assert re.search(r'<script[^>]*src="/static/core/htmx\.min\.js"', html)
        assert 'unpkg.com' not in html and 'jsdelivr' not in html
        path = finders.find('core/htmx.min.js')
        assert path, 'core/static/core/htmx.min.js deve esistere'
        with open(path, encoding='utf-8') as fh:
            assert 'version:"2.' in fh.read()

    def test_body_sends_csrf_header(self, logged):
        html = logged.get('/boards/').content.decode()
        assert re.search(r"""<body[^>]*hx-headers='\{"X-CSRFToken": "[A-Za-z0-9]{32,64}"\}'""", html)

    def test_aria_live_region(self, logged):
        html = logged.get('/boards/').content.decode()
        assert re.search(r'<div[^>]*id="annunci"[^>]*aria-live="polite"', html)

    def test_htmx_post_needs_csrf_header(self, user):
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        client.get('/boards/')
        token = client.cookies['csrftoken'].value
        senza = client.post('/boards/nuova/', {'title': 'Senza token'}, headers=HX)
        assert senza.status_code == 403
        con = client.post('/boards/nuova/', {'title': 'Con token'},
                          headers={**HX, 'X-CSRFToken': token})
        assert con.status_code == 200
        assert list(Board.objects.values_list('title', flat=True)) == ['Con token']
