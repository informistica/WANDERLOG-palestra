# Livello 08: task in background con Celery

## Obiettivo

Spostare fuori dalla richiesta HTTP il lavoro lento o che dipende da servizi esterni. In WANDERLOG lo fanno Celery e Redis (§2 del piano): parser delle email, notifiche, cambi valuta. Qui un task completa l'indirizzo di un luogo con un geocoder finto, e il service layer lo accoda solo dopo il commit.

## Cosa si allena di WANDERLOG

- L'app Celery in `palestra/celery.py`, caricata da `palestra/__init__.py` (task 0.4 del piano)
- Configurazione dalle impostazioni `CELERY_*` di Django: broker Redis (`CELERY_BROKER_URL`), risultati su Redis (`REDIS_URL`, decisione #18), solo JSON
- `@shared_task` in `places/tasks.py`, trovato con `autodiscover_tasks()`
- Il task riceve **l'id** del luogo, non l'oggetto: i messaggi passano dal broker in JSON
- Task **idempotente**: se il worker lo riesegue (ritentativo, doppio invio) non rifà il lavoro
- Ritentativi automatici per gli errori temporanei: `autoretry_for`, `retry_backoff`, `max_retries=5` (decisione #19)
- `transaction.on_commit` nel servizio: il task parte solo quando il luogo è davvero nel database
- Un adapter esterno con implementazione `mock` deterministica (`places/geocoding.py`), come gli adapter di WANDERLOG
- Nei test i task girano subito, nello stesso processo (`task_always_eager` nel `conftest.py`, decisione #38); il worker è un servizio del compose

## Prerequisiti

Livello 07 completato: lo starter parte dalla sua soluzione. `celery` e `redis` sono già nei requirements: non serve ricostruire l'immagine.

## Cosa c'è nello starter

Già pronti:

- `places/models.py`: il campo `Place.address`, con la migrazione `0002_place_address.py`
- `places/geocoding.py`: l'adapter finto (`reverse_geocode`) e l'errore temporaneo `GeocodingError`
- `palestra/celery.py`: l'oggetto `app = Celery('palestra')`
- `tests/conftest.py`: i task in modalità eager per tutti i test

Da completare:

- `palestra/settings.py`: le impostazioni `CELERY_*`
- `palestra/celery.py` e `palestra/__init__.py`
- `places/tasks.py`: `geocode_place`
- `places/services.py`: `add_place_to_board` accoda il task
- `compose.yaml`: il servizio `celery-worker`

## Cosa devi fare

1. **Impostazioni.** In `settings.py`:
   - `CELERY_BROKER_URL` da `os.environ['CELERY_BROKER_URL']` (con un default per il compose);
   - `CELERY_RESULT_BACKEND` dalla variabile `REDIS_URL`;
   - `CELERY_ACCEPT_CONTENT = ['json']`, `CELERY_TASK_SERIALIZER = 'json'`, `CELERY_RESULT_SERIALIZER = 'json'`;
   - `CELERY_TIMEZONE = TIME_ZONE`.
2. **L'app.** In `celery.py`: `app.config_from_object('django.conf:settings', namespace='CELERY')` e `app.autodiscover_tasks()`. In `palestra/__init__.py`: `from .celery import app as celery_app` e `__all__ = ('celery_app',)`.
3. **Il task.** `@shared_task(autoretry_for=(geocoding.GeocodingError,), retry_backoff=True, max_retries=5)`. `geocode_place(place_id)`:
   - se il luogo non c'è più restituisce `'missing'`;
   - se ha già un indirizzo restituisce `'skipped'` senza chiamare il provider;
   - altrimenti chiama `geocoding.reverse_geocode(place.lat, place.lng)`, salva con `update_fields=['address', 'updated_at']` e restituisce `'done'`.
   Chiama il provider come `geocoding.reverse_geocode(...)`, non importando la funzione: così i test possono sostituirlo.
4. **Il servizio.** In `add_place_to_board`, dopo la creazione: `transaction.on_commit(lambda: geocode_place.delay(str(place.id)))`. Un luogo non valido non accoda niente: la `ValueError` arriva prima.
5. **Il worker.** In `compose.yaml` aggiungi `celery-worker`: stessa immagine, `volumes`, `working_dir`, `env_file` e `depends_on` (db e redis) di `django`, senza `ports`, con `command: celery -A palestra worker -l info`.

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose run --rm django python manage.py makemigrations --check
docker compose up
```

Per provare a mano: con `docker compose up` crea un luogo dall'API (`POST /api/v1/boards/<id>/places/`). Nel log di `celery-worker` compare `Task places.tasks.geocode_place[...] succeeded ... 'done'`, e nell'admin il luogo ha l'indirizzo.

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_celery_app.py` | impostazioni dall'ambiente, app configurata da Django, `celery_app` esportata, broker Redis raggiungibile, il worker trova il task (processo separato), servizio `celery-worker` nel compose | **target dei TODO** (passi 1, 2, 5) |
| `tests/test_geocode_task.py` | il task, l'idempotenza, il luogo cancellato, `.delay()` in modalità eager, la politica dei ritentativi, `on_commit` nel servizio e nell'API | **target dei TODO** (passi 3-4) |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** (regressione): passano già sullo starter |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

La migrazione del campo `address` è già nello starter: `makemigrations --check` non deve trovare nulla.

## Suggerimenti

- Nei test pytest-django ogni test sta in una transazione che non arriva al commit: le callback di `on_commit` non partono da sole. I test usano la fixture `django_capture_on_commit_callbacks`.
- Mai passare un oggetto del modello a `.delay()`: con il serializer JSON non si può, e anche con pickle il worker leggerebbe dati vecchi. Si passa l'id e il task rilegge dal database.
- Idempotenza: il broker garantisce "almeno una volta", non "esattamente una volta". Il controllo su `address` rende innocua una seconda esecuzione.
- Senza worker avviato i task restano nella coda di Redis: `docker compose logs celery-worker` è il primo posto dove guardare.
- `places.services` importa `places.tasks`, che non importa i servizi: niente import circolari, e `lint-imports` resta verde.

## Prossimo livello

`09_channels/`: aggiornamenti in tempo reale con Django Channels.
