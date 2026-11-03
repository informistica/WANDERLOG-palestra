"""Livello 13, passi 4-9: interfaccia in italiano e in inglese."""
import re
from pathlib import Path

import polib
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import translation
from django.utils.functional import Promise

User = get_user_model()
PROJECT = Path(__file__).resolve().parents[1]
LEVEL = PROJECT.parent
PO = PROJECT / 'locale' / 'en' / 'LC_MESSAGES' / 'django.po'
MO = PO.with_suffix('.mo')
PASSWORD = 'Passw0rd-Lunga-2026'
HX = {'HX-Request': 'true'}
TEMPLATES = [
    'core/templates/base.html',
    'core/templates/core/welcome.html',
    'boards/templates/boards/board_list.html',
    'boards/templates/boards/board_detail.html',
    'boards/templates/boards/_board_form.html',
    'boards/templates/boards/_board_edit_form.html',
    'boards/templates/boards/_board_header.html',
    'boards/templates/boards/_board_list.html',
    'places/templates/places/board_map.html',
]
TRANS_RE = re.compile(r"""{%\s*trans(?:late)?\s+(["'])(.*?)\1""")
BLOCK_RE = re.compile(r'{%\s*blocktrans(?:late)?\b[^%]*%}(.*?){%\s*endblocktrans(?:late)?\s*%}', re.S)
VAR_RE = re.compile(r'{{\s*(\w+)\s*}}')


@pytest.fixture(autouse=True)
def reset_language():
    "Le richieste attivano una lingua nel thread: dopo ogni test si torna a LANGUAGE_CODE."
    yield
    translation.deactivate()


def html_lang(response):
    match = re.search(r'<html[^>]*\blang="([^"]*)"', response.content.decode())
    return match.group(1) if match else None


def make_user(email, language):
    return User.objects.create_user(email=email, password=PASSWORD, language=language)


def template_msgids():
    ids = set()
    for rel in TEMPLATES:
        text = (PROJECT / rel).read_text(encoding='utf-8')
        ids.update(m.group(2) for m in TRANS_RE.finditer(text))
        ids.update(VAR_RE.sub(r'%(\1)s', m.group(1)).strip() for m in BLOCK_RE.finditer(text))
    return ids


def load_po():
    assert PO.exists(), 'crea locale/en/LC_MESSAGES/django.po'
    return polib.pofile(str(PO))


class TestSettings:
    """Passo 4: lingue, cataloghi e middleware."""

    def test_languages(self):
        assert settings.USE_I18N is True
        assert settings.LANGUAGE_CODE == 'it'
        assert [code for code, _ in settings.LANGUAGES] == ['it', 'en']

    def test_locale_paths(self):
        paths = [Path(p).resolve() for p in settings.LOCALE_PATHS]
        assert (PROJECT / 'locale').resolve() in paths

    def test_locale_middleware_order(self):
        mw = list(settings.MIDDLEWARE)
        name = 'django.middleware.locale.LocaleMiddleware'
        assert name in mw, 'aggiungi LocaleMiddleware'
        assert mw.index('django.contrib.sessions.middleware.SessionMiddleware') < mw.index(name)
        assert mw.index(name) < mw.index('django.middleware.common.CommonMiddleware')

    def test_user_language_middleware_after_auth(self):
        mw = list(settings.MIDDLEWARE)
        name = 'core.middleware.UserLanguageMiddleware'
        assert name in mw, 'aggiungi core.middleware.UserLanguageMiddleware'
        assert mw.index('django.contrib.auth.middleware.AuthenticationMiddleware') < mw.index(name)

    def test_i18n_context_processor(self):
        processors = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        assert 'django.template.context_processors.i18n' in processors


class TestCatalog:
    """Passo 7: catalogo inglese completo e compilato, anche in CI."""

    def test_po_fully_translated(self):
        po = load_po()
        assert len(po) >= 20, 'il catalogo deve contenere tutte le stringhe tradotte'
        assert not po.untranslated_entries(), [e.msgid for e in po.untranslated_entries()]
        assert not po.fuzzy_entries(), [e.msgid for e in po.fuzzy_entries()]

    def test_mo_matches_po(self):
        assert MO.exists(), 'compila il catalogo: python manage.py compilemessages'
        po = load_po()
        mo = polib.mofile(str(MO))
        assert {e.msgid: e.msgstr for e in mo if e.msgid} == {
            e.msgid: e.msgstr for e in po.translated_entries()}, (
            'il .mo non corrisponde al .po: ricompila')

    def test_templates_use_i18n(self):
        missing = []
        for rel in TEMPLATES:
            text = (PROJECT / rel).read_text(encoding='utf-8')
            loads = re.search(r'{%\s*load\b[^%]*\bi18n\b', text)
            uses = TRANS_RE.search(text) or BLOCK_RE.search(text)
            if not (loads and uses):
                missing.append(rel)
        assert not missing, f'template ancora da tradurre: {missing}'

    def test_template_strings_are_in_catalog(self):
        ids = template_msgids()
        assert ids
        po_ids = {e.msgid for e in load_po()}
        assert not ids - po_ids, f'stringhe mancanti nel .po: {sorted(ids - po_ids)}'

    def test_ci_compiles_messages(self):
        ci = (LEVEL / '.github' / 'workflows' / 'ci.yml').read_text(encoding='utf-8')
        assert 'gettext' in ci, 'installa gettext nel job (serve a compilemessages)'
        assert 'compilemessages' in ci
        assert ci.index('compilemessages') < ci.rindex('pytest'), 'compila prima dei test'


@pytest.mark.django_db
class TestLanguagePages:
    """Passo 5: la pagina pubblica con la lingua nell'URL e la lingua del browser."""

    @pytest.mark.parametrize('prefix, text', [('/it/', 'Benvenuto'), ('/en/', 'Welcome')])
    def test_welcome_page(self, client, prefix, text):
        response = client.get(prefix)
        assert response.status_code == 200
        assert 'core/welcome.html' in [t.name for t in response.templates]
        assert text in response.content.decode()
        assert html_lang(response) == prefix.strip('/')
        assert response['Content-Language'] == prefix.strip('/')

    def test_anonymous_follows_accept_language(self, client):
        response = client.get('/accounts/login/', headers={'Accept-Language': 'en'})
        assert response.status_code == 200
        assert html_lang(response) == 'en'


@pytest.mark.django_db
class TestUserLanguage:
    """Passo 8: chi ha scelto una lingua la ritrova dopo il login."""

    def test_english_user_sees_english(self, client):
        client.force_login(make_user('en@example.com', 'en'))
        response = client.get('/boards/')
        html = response.content.decode()
        assert 'My boards' in html and 'Log out' in html
        assert html_lang(response) == 'en'
        assert response['Content-Language'] == 'en'

    def test_user_setting_beats_browser(self, client):
        client.force_login(make_user('it@example.com', 'it'))
        response = client.get('/boards/', headers={'Accept-Language': 'en'})
        assert 'Le mie bacheche' in response.content.decode()
        assert response['Content-Language'] == 'it'

    def test_language_applied_on_login(self, client):
        make_user('en@example.com', 'en')
        response = client.post('/accounts/login/',
                               {'login': 'en@example.com', 'password': PASSWORD}, follow=True)
        assert response.redirect_chain[-1][0] == '/boards/'
        assert 'My boards' in response.content.decode()

    def test_htmx_partial_errors_in_english(self, client):
        client.force_login(make_user('en@example.com', 'en'))
        response = client.post('/boards/nuova/', {'title': ''}, headers=HX)
        assert 'This field is required.' in response.content.decode()


@pytest.mark.django_db
class TestLanguageSwitcher:
    """Passo 9: il selettore della lingua."""

    def test_switcher_in_layout(self, client):
        client.force_login(make_user('it@example.com', 'it'))
        html = client.get('/boards/').content.decode()
        assert 'id="language-form"' in html and 'action="/i18n/setlang/"' in html
        assert 'name="language"' in html and 'value="en"' in html

    def test_switch_saves_user_language(self, client):
        user = make_user('it@example.com', 'it')
        client.force_login(user)
        response = client.post('/i18n/setlang/', {'language': 'en', 'next': '/boards/'})
        assert response.status_code == 302
        assert response['Location'] == '/boards/'
        assert response.cookies[settings.LANGUAGE_COOKIE_NAME].value == 'en'
        user.refresh_from_db()
        assert user.language == 'en'
        assert 'My boards' in client.get('/boards/').content.decode()

    def test_unknown_language_is_ignored(self, client):
        user = make_user('it@example.com', 'it')
        client.force_login(user)
        response = client.post('/i18n/setlang/', {'language': 'xx', 'next': '/boards/'})
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.language == 'it'

    def test_anonymous_switch_translates_prefixed_url(self, client):
        response = client.post('/i18n/setlang/', {'language': 'en', 'next': '/it/'})
        assert response.status_code == 302
        assert response['Location'] == '/en/'

    def test_get_not_allowed(self, client):
        assert client.get('/i18n/setlang/').status_code == 405


class TestLazyStrings:
    """Passo 6: modelli e form con gettext_lazy."""

    def test_model_verbose_names(self):
        from boards.models import Board, Collaborator
        from places.models import Place
        assert isinstance(Board._meta.get_field('title').verbose_name, Promise)
        with translation.override('en'):
            assert str(Board._meta.get_field('title').verbose_name) == 'Title'
            assert str(Board._meta.verbose_name_plural) == 'Boards'
            assert str(Place._meta.get_field('lat').verbose_name) == 'Latitude'
            assert str(dict(Collaborator.ROLE_CHOICES)[Collaborator.ROLE_VIEWER]) == 'Viewer'
        with translation.override('it'):
            assert str(Board._meta.get_field('title').verbose_name) == 'Titolo'

    def test_form_help_text(self):
        from boards.forms import BoardForm
        with translation.override('en'):
            assert str(BoardForm().fields['title'].help_text) == 'For example: A weekend in Rome'
        with translation.override('it'):
            assert str(BoardForm().fields['title'].help_text) == 'Per esempio: Weekend a Roma'