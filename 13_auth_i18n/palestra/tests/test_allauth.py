"""Livello 13, passi 1-3: account con django-allauth (login con email, signup, logout)."""
from pathlib import Path

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import NoReverseMatch, reverse

User = get_user_model()
LEVEL = Path(__file__).resolve().parents[2]
PASSWORD = 'Passw0rd-Lunga-2026'
MISSING = object()


def template_names(response):
    return [t.name for t in response.templates]


def logged_user_id(client):
    return client.session.get('_auth_user_id')


@pytest.fixture
def member(db):
    return User.objects.create_user(email='mario@example.com', password=PASSWORD)


class TestSetup:
    """Passo 1: pacchetto, app, middleware e backend."""

    def test_allauth_in_requirements(self):
        lines = (LEVEL / 'requirements.txt').read_text(encoding='utf-8').lower().splitlines()
        names = [ln.split('#')[0].strip() for ln in lines]
        assert any(n.startswith('django-allauth') for n in names), (
            'aggiungi django-allauth a requirements.txt')

    def test_apps_installed_before_project_apps(self):
        apps = list(settings.INSTALLED_APPS)
        assert 'allauth' in apps and 'allauth.account' in apps, 'installa allauth e allauth.account'
        assert apps.index('allauth') < apps.index('allauth.account') < apps.index('core')
        assert 'django.contrib.sites' not in apps, 'allauth 65 non richiede django.contrib.sites'

    def test_account_middleware(self):
        mw = list(settings.MIDDLEWARE)
        name = 'allauth.account.middleware.AccountMiddleware'
        assert name in mw, 'aggiungi AccountMiddleware'
        assert mw.index('django.contrib.auth.middleware.AuthenticationMiddleware') < mw.index(name)

    def test_authentication_backends(self):
        backends = list(getattr(settings, 'AUTHENTICATION_BACKENDS', []))
        assert 'allauth.account.auth_backends.AuthenticationBackend' in backends
        assert 'django.contrib.auth.backends.ModelBackend' in backends, (
            "tieni ModelBackend: serve all'admin e a force_login")


class TestSettings:
    """Passo 2: login con email e redirect verso le URL di allauth."""

    def test_email_login_without_username(self):
        assert getattr(settings, 'ACCOUNT_USER_MODEL_USERNAME_FIELD', MISSING) is None
        assert getattr(settings, 'ACCOUNT_LOGIN_METHODS', None) == {'email'}
        assert getattr(settings, 'ACCOUNT_SIGNUP_FIELDS', None) == [
            'email*', 'password1*', 'password2*']
        assert getattr(settings, 'ACCOUNT_EMAIL_VERIFICATION', None) in ('optional', 'mandatory')

    def test_redirects_use_allauth_names(self):
        assert settings.LOGIN_URL == 'account_login'
        assert settings.LOGIN_REDIRECT_URL == 'boards:list'
        assert settings.LOGOUT_REDIRECT_URL == 'account_login'

    @pytest.mark.parametrize('name, path', [
        ('account_login', '/accounts/login/'),
        ('account_signup', '/accounts/signup/'),
        ('account_logout', '/accounts/logout/'),
    ])
    def test_allauth_urls(self, name, path):
        try:
            assert reverse(name) == path
        except NoReverseMatch:
            pytest.fail(f"manca la URL {name}: includi allauth.urls sotto accounts/")


@pytest.mark.django_db
class TestPages:
    """Passi 2-3: le pagine di allauth, con il layout del progetto."""

    def test_login_page_uses_project_layout(self, client):
        response = client.get('/accounts/login/')
        assert response.status_code == 200
        assert response.resolver_match.url_name == 'account_login'
        names = template_names(response)
        assert 'account/login.html' in names
        assert 'allauth/layouts/base.html' in names and 'base.html' in names, (
            'templates/allauth/layouts/base.html deve estendere base.html')
        html = response.content.decode()
        assert 'name="login"' in html and 'name="password"' in html

    def test_login_with_email(self, client, member):
        response = client.post('/accounts/login/',
                               {'login': 'mario@example.com', 'password': PASSWORD})
        assert response.status_code == 302
        assert response['Location'] == '/boards/'
        assert logged_user_id(client) == str(member.pk)

    def test_wrong_password_shows_error(self, client, member):
        response = client.post('/accounts/login/',
                               {'login': 'mario@example.com', 'password': 'sbagliata'})
        assert response.status_code == 200
        assert 'account/login.html' in template_names(response)
        assert response.context['form'].errors
        assert logged_user_id(client) is None

    def test_signup_form_has_no_username(self, client):
        response = client.get('/accounts/signup/')
        assert response.status_code == 200
        html = response.content.decode()
        assert 'name="email"' in html and 'name="password2"' in html
        assert 'name="username"' not in html

    def test_signup_creates_user_and_sends_confirmation(self, client):
        response = client.post('/accounts/signup/', {
            'email': 'nuova@example.com', 'password1': PASSWORD, 'password2': PASSWORD})
        assert response.status_code == 302
        assert response['Location'] == '/boards/'
        user = User.objects.get(email='nuova@example.com')
        assert user.check_password(PASSWORD)
        from allauth.account.models import EmailAddress
        assert EmailAddress.objects.filter(user=user, email='nuova@example.com').exists()
        assert len(mail.outbox) == 1 and mail.outbox[0].to == ['nuova@example.com']

    def test_logout_with_allauth(self, client, member):
        client.force_login(member)
        response = client.post('/accounts/logout/')
        assert response.resolver_match.url_name == 'account_logout'
        assert response.status_code == 302
        assert response['Location'] == '/accounts/login/'
        assert logged_user_id(client) is None

    def test_protected_page_redirects_to_allauth_login(self, client):
        response = client.get('/boards/')
        assert response.status_code == 302
        assert response['Location'] == reverse('account_login') + '?next=/boards/'