# Livello 09: tempo reale con Django Channels

## Obiettivo

Chi tiene aperta una bacheca vede comparire i luoghi aggiunti dagli altri senza ricaricare la pagina. Come in WANDERLOG (task 0.6 e 1A.5 del piano), le scritture restano su HTTP. Il WebSocket **riceve soltanto** (decisione #22): dopo il commit il service layer manda un evento al gruppo `board_<id>`, e il consumer lo trasforma in un frammento HTML che htmx inserisce nella lista.

## Cosa si allena di WANDERLOG

- Django come applicazione ASGI: `daphne` come prima app, `ASGI_APPLICATION`, `asgi.py` con `ProtocolTypeRouter`
- Sicurezza del WebSocket: `AllowedHostsOriginValidator` (origine) e `AuthMiddlewareStack` (utente dalla sessione)
- Channel layer su Redis (`channels_redis`, database 1 con `CHANNEL_LAYER_URL`). Nei test si usa quello in memoria (decisione #38), più un test sul Redis vero
- Gruppi: un gruppo per bacheca, `board_<id>`
- Messaggio `{"type": "board.event", "payload": {...}}` e metodo `board_event` del consumer (decisione #23)
- Le **policy** del livello 04 si riusano alla connessione e si **ricontrollano a ogni evento** (decisione #24): un collaboratore rimosso smette di ricevere
- `transaction.on_commit` per la diffusione, come per il task Celery del livello 08
- L'estensione `ws` di htmx vendorizzata e caricata solo sulla pagina della bacheca, con swap out-of-band
- Test sincroni con `async_to_sync` e `WebsocketCommunicator`, **senza pytest-asyncio** (decisione #25)

## Prerequisiti

Livello 08 completato: lo starter parte dalla sua soluzione. Ci sono tre dipendenze nuove (`channels`, `channels-redis`, `daphne`), quindi ricostruisci l'immagine. Aggiungi `CHANNEL_LAYER_URL` al tuo `.env`, come in `.env.example`.

```bash
docker compose build
```

## Cosa c'è nello starter

Già pronti:

- `requirements.txt` con le dipendenze di Channels
- `boards/routing.py`: l'URL `ws/boards/<uuid>/`
- `core/static/core/ext/ws.js`: l'estensione htmx-ext-ws 2.0.4 (licenza 0BSD)
- `tests/conftest.py`: la fixture `inmemory_channel_layer`

Da completare:

- `palestra/settings.py`
- `boards/realtime.py`
- `boards/consumers.py`
- `boards/templates/boards/_place_oob.html`
- `boards/templates/boards/board_detail.html`
- `palestra/asgi.py`
- `places/services.py`

## Cosa devi fare

1. **Impostazioni.**
   - `'daphne'` come **prima** voce di `INSTALLED_APPS`: `runserver` diventa il server ASGI.
   - `ASGI_APPLICATION = 'palestra.asgi.application'`.
   - `CHANNEL_LAYERS` con `channels_redis.core.RedisChannelLayer` e `CONFIG = {'hosts': [<CHANNEL_LAYER_URL>]}`.
2. **Gruppo e invio** (`boards/realtime.py`).
   - `board_group(board_id)` restituisce `'board_<id>'`.
   - `broadcast_board_event(board_id, payload)` chiama `group_send` con `{'type': 'board.event', 'payload': payload}`. `group_send` è asincrona e il service layer è sincrono: usa `async_to_sync`.
   - In `add_place_to_board`, trasforma la callback del livello 08 in una funzione `after_commit` che accoda il task e poi chiama `broadcast_board_event(board.id, {'event': 'place.added', 'place': {'id': str(place.id), 'name': place.name}})`. Resta una sola `transaction.on_commit`: i test del livello 08 contano le callback. Il payload contiene solo stringhe: passa da Redis.
3. **Il consumer** (`boards/consumers.py`).
   - `board_visible()` (già decorato con `database_sync_to_async`): la bacheca esiste e `can_view_board(self.scope['user'], board)`.
   - `connect`: se la bacheca non è visibile chiudi con `FORBIDDEN` (4403); altrimenti `group_add` e `accept`.
   - `disconnect`: `group_discard`.
   - `board_event`: ricontrolla la visibilità. Se è persa chiudi con `FORBIDDEN`, altrimenti manda il frammento HTML.
   - `receive` resta vuoto.
4. **La pagina.**
   - `_place_oob.html`:
     - un `<ul hx-swap-oob="beforeend:#place-list">` con `<li id="place-<id>"><nome></li>`;
     - `<li id="place-empty" hx-swap-oob="delete"></li>`, per togliere il messaggio "Nessun luogo".
   - In `board_detail.html`:
     - avvolgi la lista in `<section hx-ext="ws" ws-connect="/ws/boards/<id>/">`;
     - dai gli id ai `<li>`;
     - carica `core/ext/ws.js` (con `defer`) nel blocco `scripts`.
5. **ASGI** (`palestra/asgi.py`): `ProtocolTypeRouter` con `'http'` a `django_asgi_app` e `'websocket'` a `AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns)))`.

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose up
```

Per provare a mano:

1. Apri la stessa bacheca in due finestre, con il proprietario e con un collaboratore.
2. Aggiungi un luogo dall'API (`POST /api/v1/boards/<id>/places/`).
3. Il luogo compare in entrambe le finestre. Nel log di `django` si vede `WebSocket CONNECT /ws/boards/...`.

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_realtime.py` | impostazioni ASGI e channel layer Redis (andata e ritorno su Redis vero), gruppo e invio, invio solo dopo il commit, consumer: proprietario e collaboratore ricevono, estraneo/anonimo/bacheca inesistente rifiutati con 4403, permesso ricontrollato a ogni evento, messaggi del browser ignorati, uscita dal gruppo, dal servizio al browser; applicazione ASGI con cookie di sessione e origine; frammento e pagina | **target dei TODO** (passi 1-5) |
| `tests/test_celery_app.py`, `tests/test_geocode_task.py` | livello 08 | **test di controllo** (regressione): passano già sullo starter |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

## Suggerimenti

- Niente pytest-asyncio: ogni test scrive uno scenario `async def` e lo esegue con `async_to_sync(scenario)()`. Leggi `tests/test_realtime.py` come esempio.
- `database_sync_to_async` chiude le connessioni vecchie al database. I test che passano dal consumer usano `django_db(transaction=True)`. Lì non c'è la transazione del test, quindi `on_commit` parte subito.
- Il codice prima di `accept()` decide: chiudere in `connect` rifiuta la connessione, e il client vede il codice 4403.
- Nel consumer non importare `places`: `boards` sta sotto `places` nei layer di `lint-imports`. Il frammento usa i dati del payload.
- `{{ place.name }}` nel template viene escapato: un nome con `<script>` arriva come testo.
- htmx tratta ogni messaggio del WebSocket come contenuto out-of-band: senza `hx-swap-oob` non succede niente.

## Prossimo livello

`10_email/`: luoghi inviati per email e notifiche con Mailpit.
