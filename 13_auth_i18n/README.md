# Livello 13: account con allauth e interfaccia it/en

## Obiettivo

Fino al livello 12 il login e' quello di Django, con il form `username`/`password`, e l'interfaccia e' solo in italiano. In WANDERLOG gli account sono di **django-allauth**: si entra con l'email, ci si registra da soli e si esce con un POST. L'interfaccia e' in **italiano e inglese**: la lingua arriva dall'URL (`/it/`, `/en/`) sulle pagine pubbliche, dal browser per chi non e' entrato, dal profilo (`User.language`) per chi ha fatto il login.

## Cosa si allena di WANDERLOG

- `django-allauth`: app `allauth` e `allauth.account`, `AccountMiddleware`, backend di autenticazione, `include('allauth.urls')`
- login con email e niente username: `ACCOUNT_LOGIN_METHODS`, `ACCOUNT_SIGNUP_FIELDS`, `ACCOUNT_USER_MODEL_USERNAME_FIELD`, `ACCOUNT_EMAIL_VERIFICATION`
- redirect per nome di URL: `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
- le pagine di allauth dentro il layout del progetto (`templates/allauth/layouts/base.html`)
- i18n di Django: `LANGUAGES`, `LOCALE_PATHS`, `LocaleMiddleware`, `i18n_patterns`, `{% translate %}` e `{% blocktranslate %}`, `gettext_lazy`
- il catalogo `locale/en/LC_MESSAGES/django.po`, `compilemessages` e il file `.mo`
- un middleware che applica la lingua dell'utente e un selettore della lingua che la salva

## Prerequisiti

Livello 12 completato: lo starter parte dalla sua soluzione. Il modello `User` ha gia' il campo `language` (`'it'` o `'en'`, livello 02).

## Cosa c'e' nello starter

Gia' pronti: tutto il codice dei livelli 01-12, i test bersaglio `tests/test_allauth.py` e `tests/test_i18n.py`, il template `core/templates/core/welcome.html` (ancora da tradurre) e il catalogo `palestra/locale/en/LC_MESSAGES/django.po` con tutti i `msgid` in italiano e i `msgstr` vuoti.

Da completare (cerca `TODO` nei file):

- `requirements.txt`
- `palestra/palestra/settings.py` e `palestra/palestra/urls.py`
- `palestra/core/middleware.py` e `palestra/core/views.py` (stub)
- `palestra/core/templates/base.html` e i template di `boards` e `places`
- `palestra/boards/models.py`, `palestra/places/models.py`, `palestra/boards/forms.py`
- `palestra/locale/en/LC_MESSAGES/django.po`
- `.github/workflows/ci.yml`
- un file nuovo: `palestra/templates/allauth/layouts/base.html`

## Cosa devi fare

1. **Installa allauth.** In `requirements.txt` aggiungi `django-allauth>=65.0,<66`. In `INSTALLED_APPS` metti `allauth` e `allauth.account` prima delle app del progetto (non serve `django.contrib.sites`). In `MIDDLEWARE` aggiungi `allauth.account.middleware.AccountMiddleware` in fondo. In `AUTHENTICATION_BACKENDS` tieni `django.contrib.auth.backends.ModelBackend` (admin, `force_login`) e aggiungi `allauth.account.auth_backends.AuthenticationBackend`. Poi `docker compose build`.
2. **Login con email.** Impostazioni:
   - `ACCOUNT_USER_MODEL_USERNAME_FIELD = None` (il nostro `User` non ha `username`);
   - `ACCOUNT_LOGIN_METHODS = {'email'}`;
   - `ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']`;
   - `ACCOUNT_EMAIL_VERIFICATION = 'optional'` (vedi le differenze con WANDERLOG in fondo);
   - `LOGIN_URL = 'account_login'`, `LOGOUT_REDIRECT_URL = 'account_login'`, `LOGIN_REDIRECT_URL = 'boards:list'`.

   In `urls.py` sostituisci `include('django.contrib.auth.urls')` con `include('allauth.urls')`, sempre sotto `accounts/`: i percorsi `/accounts/login/` e `/accounts/logout/` restano gli stessi, si aggiunge `/accounts/signup/`. Dopo `migrate` ci sono le tabelle di allauth (`account_emailaddress`).
3. **Le pagine di allauth nel nostro layout.** Crea `palestra/templates/allauth/layouts/base.html` che estende `base.html` e riempie i suoi blocchi con quelli di allauth: `head_title` nel `title`, `extra_head` nell'`head`, `content` nel `content`, `extra_body` negli `scripts`. Aggiungi `BASE_DIR / 'templates'` a `TEMPLATES['DIRS']`. In `base.html` il form di logout fa POST a `{% url 'account_logout' %}`; per chi non e' entrato metti i link ad `account_login` e `account_signup`. Il vecchio `core/templates/registration/login.html` non serve piu': puoi cancellarlo.
4. **Le lingue.** `LANGUAGE_CODE = 'it'`, `LANGUAGES = [('it', 'Italiano'), ('en', 'English')]`, `LOCALE_PATHS = [BASE_DIR / 'locale']`. `django.middleware.locale.LocaleMiddleware` va dopo `SessionMiddleware` e prima di `CommonMiddleware`. Nei `context_processors` aggiungi `django.template.context_processors.i18n`.
5. **Traduci i template.** In `base.html`, nei template di `boards` (`board_list`, `board_detail`, `_board_form`, `_board_edit_form`, `_board_header`, `_board_list`), in `places/board_map.html` e in `core/welcome.html`: `{% load i18n %}`, poi `{% translate "..." %}` per i testi fissi e `{% blocktranslate with email=board.owner.email %}Proprietario: {{ email }}{% endblocktranslate %}` per quelli con variabili. Il `msgid` e' il testo italiano: deve essere identico a quello del `.po`. In `base.html` `<html lang="{{ LANGUAGE_CODE }}">`. Poi la pagina pubblica: in `urls.py` aggiungi con `i18n_patterns(...)` la pagina `welcome` (`TemplateView` con `core/welcome.html`), che risponde su `/it/` e `/en/`. Le pagine dell'app restano senza prefisso.
6. **Modelli e form.** `from django.utils.translation import gettext_lazy as _` e `verbose_name=_('Titolo')` e cosi' via in `boards/models.py` e `places/models.py` (anche `Meta.verbose_name`, `verbose_name_plural` e l'etichetta di `ROLE_CHOICES`); in `boards/forms.py` l'`help_text` del titolo. Con `gettext` (non lazy) la stringa verrebbe tradotta una volta sola, all'import, nella lingua di quel momento. Le stringhe non cambiano: `makemigrations --check` resta pulito.
7. **Il catalogo inglese.** Riempi i `msgstr` di `locale/en/LC_MESSAGES/django.po` (niente voci vuote o `fuzzy`; nelle voci con `%(email)s` o `%(title)s` il segnaposto resta uguale). Poi compila:
   ```bash
   docker compose run --rm django python manage.py compilemessages
   ```
   Nasce `django.mo`, il file che Django legge davvero: va nel repository insieme al `.po`. Nella CI (`.github/workflows/ci.yml`) aggiungi uno step che installa `gettext` (`sudo apt-get update && sudo apt-get install -y gettext`) e uno, in `palestra/`, con `python manage.py compilemessages` prima di `pytest`.
8. **La lingua dell'utente.** In `core/middleware.py` completa `UserLanguageMiddleware`: se l'utente e' autenticato, `user.language` e' una delle `LANGUAGES` e il percorso non ha il prefisso di lingua (`translation.get_language_from_path`), chiama `translation.activate(user.language)` e imposta `request.LANGUAGE_CODE`. Mettilo in `MIDDLEWARE` subito dopo `AuthenticationMiddleware`. Cosi' l'utente inglese vede l'inglese appena entra, anche se il suo browser e' in italiano.
9. **Il selettore della lingua.** In `core/views.py` scrivi `set_language`: solo POST (`@require_POST`), chiama `django.views.i18n.set_language` (cookie e redirect a `next`) e, se l'utente e' autenticato e la lingua e' valida, la salva in `request.user.language` (`save(update_fields=['language'])`). In `urls.py`: `path('i18n/setlang/', set_language, name='set_language')`. In `base.html` un `<form id="language-form" method="post" action="{% url 'set_language' %}">` con `csrf_token`, un `input` nascosto `next` con `request.get_full_path`, una `<select name="language">` con le lingue di `get_available_languages` (o `get_language_info_list`) e un bottone.

```bash
docker compose build
docker compose run --rm django python manage.py migrate
docker compose run --rm django python manage.py compilemessages
docker compose run --rm django pytest tests/test_allauth.py tests/test_i18n.py -v
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose run --rm django ruff check ..
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_allauth.py` | `django-allauth` nei requisiti, app, `AccountMiddleware`, backend; impostazioni `ACCOUNT_*` e redirect; URL `account_login`, `account_signup`, `account_logout`; pagina di login di allauth dentro `base.html`; login con email, password sbagliata, registrazione con `EmailAddress` ed email di conferma, logout, redirect al login di allauth | **target dei TODO** (passi 1-3) |
| `tests/test_i18n.py` | `LANGUAGES`, `LOCALE_PATHS`, ordine dei middleware, context processor; `.po` tutto tradotto, `.mo` uguale al `.po`, template con `{% load i18n %}` e stringhe tutte nel catalogo, CI con `gettext` e `compilemessages`; `/it/` e `/en/`, `Accept-Language`, lingua dell'utente dopo il login (anche nei partial HTMX); selettore che salva la lingua; `verbose_name` e `help_text` lazy | **target dei TODO** (passi 4-9) |
| `tests/test_htmx_base.py` | livello 06; la classe `TestLogin` e' adattata (vedi sotto) | **test di controllo** |
| `tests/test_teamwork.py` | livello 12 | **test di controllo** (regressione): passa gia' sullo starter |
| `tests/test_factories.py`, `tests/test_fixtures.py`, `tests/test_tooling.py`, `tests/test_policy_matrix.py` | livello 11 | **test di controllo** |
| `tests/test_inbox.py` | livello 10 | **test di controllo** |
| `tests/test_realtime.py` | livello 09 | **test di controllo** |
| `tests/test_celery_app.py`, `tests/test_geocode_task.py` | livello 08 | **test di controllo** |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** |
| `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

**Adattamento di un test di controllo.** In `tests/test_htmx_base.py` la classe `TestLogin` del livello 06 controllava `LOGIN_URL == '/accounts/login/'` e il campo `username`. Con allauth il valore e' il nome `'account_login'` e il campo si chiama `login`. Ora il test risolve i redirect con `resolve_url` (che confronta i percorsi, non come sono scritti) e accetta `username` o `login`: passa sullo starter e sulla soluzione. Le regole nuove le controlla `tests/test_allauth.py`.

## Suggerimenti

- Il `msgid` e' la chiave: basta uno spazio diverso tra template e `.po` e la stringa resta in italiano. `{% blocktranslate %}` diventa `%(nome)s` nel catalogo.
- Dopo ogni modifica al `.po` ricompila: Django legge solo il `.mo`, e lo carica all'avvio (riavvia `runserver`).
- `makemessages -l en` (serve `gettext`, che c'e' nell'immagine Docker) ricrea il `.po` dai template e dal codice; `compilemessages` lo compila. Senza Docker, su Windows, puoi compilare con `polib` (e' in `requirements-dev.txt`): `python -c "import polib; polib.pofile('locale/en/LC_MESSAGES/django.po').save_as_mofile('locale/en/LC_MESSAGES/django.mo')"` da `palestra/`.
- L'ordine dei middleware conta: `LocaleMiddleware` sceglie la lingua da URL, cookie e `Accept-Language`; il tuo middleware, dopo l'autenticazione, la sostituisce con quella del profilo; il prefisso `/it/` o `/en/` nell'URL vince su tutto.
- allauth ha gia' i suoi cataloghi it/en: le pagine di login e registrazione si traducono da sole.
- Con `ACCOUNT_EMAIL_VERIFICATION = 'optional'` la registrazione manda comunque l'email di conferma (in sviluppo la vedi in Mailpit, livello 10) ma lascia entrare subito.

## Differenze con WANDERLOG

- WANDERLOG usa `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` (decisione #27). Qui e' `optional`, perche' gli utenti creati da factory e fixture non hanno un'email verificata e i test dei livelli precedenti non potrebbero entrare. Se vuoi provarla, mettila a `mandatory` e guarda cosa succede al login.
- WANDERLOG ha anche il login con Google (`allauth.socialaccount`): serve un client OAuth vero, quindi qui non c'e'.
- In WANDERLOG le email di allauth partono con Celery (un `ACCOUNT_ADAPTER` che chiama il task del livello 10); qui partono subito.
- Le notifiche WebSocket (livello 09) e le stringhe di `map.js` non sono tradotte; WANDERLOG passa la lingua al client (per esempio `?lang=`).

## Fine della palestra

Hai finito i 13 livelli. Il prossimo passo e' WANDERLOG vero: le stesse regole, su un progetto tuo.