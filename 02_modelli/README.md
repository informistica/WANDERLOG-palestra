# Livello 02: modelli (custom user, Board, Place)

## Obiettivo

Creare i modelli del dominio "bacheca dei luoghi preferiti" con le convenzioni di WANDERLOG: custom user con email come identificativo, chiavi primarie UUID, un modello base astratto con i timestamp.

## Cosa si allena di WANDERLOG

- Task 0.3 (custom user e registrazione delle app, prima della prima migrazione)
- `core.models.BaseModel` con UUID e `created_at`/`updated_at`
- Admin Django per i modelli

## Prerequisiti

Livello 01 completato: questo starter parte dalla sua soluzione (`Dockerfile` e `compose.yaml` sono già completi).

## Cosa c'è nello starter

- le app `core`, `boards` e `places` con i modelli da completare
- `settings.py` senza le app del progetto e senza `AUTH_USER_MODEL`
- nessuna migrazione: le crei tu

## Cosa devi fare

1. `core/models.py`: in `BaseModel` aggiungi `id` (UUID, primary key, `default=uuid.uuid4`, non modificabile), `created_at` (`auto_now_add`) e `updated_at` (`auto_now`).
2. `boards/models.py`: completa `User` (niente `username`, `id` UUID, `email` unica, `name`, `language` con scelte `it`/`en` e default `it`, `USERNAME_FIELD = 'email'`, `REQUIRED_FIELDS = []`, `objects = UserManager()`) e `Board` (`title`, `description` opzionale, `owner` con `related_name='boards'`).
3. `places/models.py`: completa `Place` (`name`, `lat`, `lng`, `description` opzionale, `board` verso `'boards.Board'` con `related_name='places'`).
4. `settings.py`: aggiungi `core`, `boards`, `places` a `INSTALLED_APPS` e imposta `AUTH_USER_MODEL = 'boards.User'`.
5. `boards/admin.py` e `places/admin.py`: registra `User` con un `UserAdmin` adattato (senza `username`: `ordering`, `list_display`, `fieldsets`, `add_fieldsets`), `Board` e `Place`.
6. Crea le migrazioni:

```bash
docker compose run --rm django python manage.py makemigrations boards places
docker compose run --rm django python manage.py migrate
docker compose run --rm django pytest
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_models.py` | campi, `__str__`, related name, custom user | **target dei TODO** (passi 1-4) |
| `tests/test_admin.py` | modelli registrati, pagina "aggiungi utente" dell'admin | **target dei TODO** (passo 5) |
| `tests/test_migrations.py` | le migrazioni esistono e sono allineate ai modelli | **target dei TODO** (passo 6) |
| `tests/test_environment.py`, `tests/test_docker_config.py` | ambiente e Docker del livello 01 | **test di controllo** (regressione del livello 01): passano già sullo starter se l'ambiente è a posto |

## Criteri di successo

- `python manage.py makemigrations --check --dry-run` non trova modifiche
- tutti i test passano

## Suggerimenti

- Il custom user va deciso prima della prima `migrate`: se avevi già migrato il database con l'utente di Django, ricrealo con `docker compose down -v`.
- `UserAdmin` di Django ordina per `username`: senza quel campo la pagina dell'admin va in errore finché non imposti `ordering`.

## Prossimo livello

`03_servizi/`: service layer e import-linter.
