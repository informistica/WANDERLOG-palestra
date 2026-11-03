# Livello 06: template Django e HTMX

## Obiettivo

Costruire le pagine HTML delle bacheche con i template di Django e HTMX, senza React e senza build JavaScript. È lo schema di WANDERLOG (§2 e §12 del piano, decisione #63): HTMX 2 come file statico versionato, un solo `base.html`, partial restituiti quando la richiesta arriva da HTMX, stesse policy e stessi servizi dell'API.

## Cosa si allena di WANDERLOG

- HTMX 2 **vendorizzato** in `core/static/core/htmx.min.js` (versione fissata, niente CDN, niente Node)
- Riconoscere HTMX dall'header `HX-Request` con una funzione di `core`, senza `django-htmx`
- Un layout `core/templates/base.html` con `hx-headers` che manda il token CSRF nell'header `X-CSRFToken` e una regione `aria-live` per gli annunci
- Template per app in `<app>/templates/<app>/`; i partial hanno il nome che inizia con `_`
- Stessa view, due risposte: pagina completa senza `HX-Request`, solo il frammento con `HX-Request: true`
- Le view HTML chiamano le stesse policy e gli stessi servizi dell'API: estraneo **404**, lettore che prova a modificare **403**
- Form che funzionano anche senza JavaScript (`method` e `action`), potenziati da `hx-post`

## Prerequisiti

Livello 05 completato: lo starter parte dalla sua soluzione. Nessun pacchetto nuovo: non serve ricostruire l'immagine.

## Cosa c'è nello starter

Già pronti:

- `core/static/core/htmx.min.js`: HTMX 2.0.11, scaricato dal pacchetto npm `htmx.org` (file di terze parti: non va modificato)
- `boards/urls.py` e `palestra/urls.py`: le rotte `/boards/...` e il login di Django sotto `/accounts/`
- `boards/templates/boards/board_list.html` e `board_detail.html`: le pagine complete, che includono i partial

Da completare:

- `palestra/settings.py`: `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
- `core/templates/registration/login.html`: il form di login
- `core/htmx.py`: `is_htmx`
- `core/templates/base.html`: script HTMX, `hx-headers` con il CSRF, regione `aria-live`
- `boards/forms.py`: `BoardForm`
- `boards/services.py`: `update_board`
- `boards/templates/boards/_board_list.html`, `_board_form.html`, `_board_header.html`, `_board_edit_form.html`: i partial
- `boards/views_html.py`: le quattro view

## Le pagine

| URL | Metodo | Senza HTMX | Con `HX-Request: true` |
|---|---|---|---|
| `/boards/` | GET | pagina `board_list.html` | partial `_board_list.html` |
| `/boards/nuova/` | POST | redirect a `/boards/` (errori: pagina con il form) | partial `_board_list.html` (errori: `_board_form.html` + `HX-Retarget: #board-form`) |
| `/boards/<id>/` | GET | pagina `board_detail.html` | pagina `board_detail.html` |
| `/boards/<id>/modifica/` | POST | redirect al dettaglio (errori: pagina con il form) | partial `_board_header.html` (errori: `_board_edit_form.html` + `HX-Retarget: #board-edit-form`) |

| Chi | Lista | Dettaglio | Modifica |
|---|---|---|---|
| Anonimo | redirect al login | redirect al login | redirect al login |
| Estraneo | non la vede | 404 | 404 |
| Collaboratore (`viewer`) | la vede | 200, senza form di modifica | 403 |
| Proprietario | la vede | 200, con form di modifica | 200 / 302 |

## Cosa devi fare

1. **Login.** In `settings.py`: `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'boards:list'`, `LOGOUT_REDIRECT_URL = 'login'`. In `registration/login.html` scrivi il form: POST verso `{% url 'login' %}`, `{% csrf_token %}`, `{{ form.as_p }}`, campo nascosto `next`. Per provare crea un utente con `docker compose run --rm django python manage.py createsuperuser`.
2. **`is_htmx(request)`.** Restituisce `True` solo se l'header `HX-Request` vale `'true'`.
3. **`base.html`.**
   - `<script src="{% static 'core/htmx.min.js' %}" defer></script>` nell'`<head>`;
   - sul `<body>`: `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'`, così ogni richiesta HTMX passa il controllo CSRF;
   - `<div id="annunci" aria-live="polite"></div>` prima del `<main>`.
4. **Form e servizio.** `BoardForm` con i campi `title` e `description`. `update_board(board, title, description="", *, requesting_user)`: `PermissionError` se `can_edit_board` dice no, `ValueError` se il titolo è vuoto dopo lo `strip`, altrimenti salva.
5. **Partial.** Rispetta gli `id`: sono i bersagli di HTMX e i test li cercano.
   - `_board_list.html`: `<ul id="board-list">`, un link per bacheca, "Nessuna bacheca, per ora." se è vuota;
   - `_board_form.html`: `<form id="board-form" method="post" action=... hx-post=... hx-target="#board-list" hx-swap="outerHTML">`;
   - `_board_header.html`: `<section id="board-header">` con titolo, descrizione e proprietario;
   - `_board_edit_form.html`: `<form id="board-edit-form" ... hx-target="#board-header" hx-swap="outerHTML">`.
6. **Lista e creazione.** Tutte le view con `@login_required`, quelle di scrittura con `@require_POST`. `board_list` e `board_create` seguono la tabella delle pagine. Con un form non valido HTMX deve sostituire il form, non la lista: usa `_retarget(response, '#board-form')`.
7. **Dettaglio e modifica.** `get_object_or_404` su `boards_visible_to(request.user)` dà il 404 agli estranei. In `board_edit` controlla `can_edit_board` prima di validare il form (`PermissionDenied`, quindi 403), poi salva con `update_board`.

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose run --rm django python manage.py makemigrations --check
docker compose up
```

Per provare a mano: apri `http://localhost:8000/boards/`, entra, crea una bacheca e guarda nella scheda Rete del browser che la risposta è solo il frammento `<ul id="board-list">`.

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_htmx_base.py` | login e redirect, `is_htmx`, `base.html` (HTMX locale, `hx-headers` CSRF, `aria-live`), POST HTMX con e senza token CSRF | **target dei TODO** (passi 1-3) |
| `tests/test_board_pages.py` | login obbligatorio, lista e creazione (pagina o partial), dettaglio e modifica con la matrice dei permessi, `update_board` | **target dei TODO** (passi 4-7) |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** (regressione): passano già sullo starter |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

Questo livello non cambia i modelli: `makemigrations --check` deve continuare a non trovare nulla.

## Suggerimenti

- HTMX 2 non sostituisce il contenuto per le risposte 4xx: per questo un form non valido risponde 200 con gli header `HX-Retarget` e `HX-Reswap`.
- Nel test client di Django il controllo CSRF è spento: il test che lo verifica usa `Client(enforce_csrf_checks=True)`.
- In `board_edit` non passare `instance=board` al form: `is_valid()` scriverebbe i dati nella bacheca prima che il servizio decida.
- `views_html.py` importa `core.htmx`: `boards` può usare `core`, il contratto `lint-imports` resta rispettato.

## Prossimo livello

`07_mappa/`: la mappa dei luoghi della bacheca.
