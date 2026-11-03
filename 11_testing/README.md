# Livello 11: test che si scrivono da soli

## Obiettivo

Dieci livelli di test hanno creato utenti, bacheche e luoghi a mano, ogni volta in modo un po' diverso. Qui si mette ordine: **factory** per creare dati validi in una riga, **fixture** condivise in `conftest.py`, un test **parametrizzato** al posto di dodici quasi uguali, e una **soglia di copertura** che fa fallire `pytest` se il codice non testato cresce troppo.

## Cosa si allena di WANDERLOG

- `factory_boy`: `DjangoModelFactory`, `Sequence`, `Faker`, `SubFactory`, `PostGenerationMethodCall`, hook `post_generation`, `build()` contro `create()`, `create_batch()`
- Fixture di pytest in `tests/conftest.py`: function scope, fixture che dipendono da altre fixture, il fixture `client` di pytest-django e l'`APIClient` di DRF
- `@pytest.mark.parametrize` con id leggibili: la matrice ruoli x azioni delle policy del livello 04
- `pytest-cov`: `--cov`, `--cov-report=term-missing`, `--cov-fail-under=80`, e un `.coveragerc` che dice cosa misurare e cosa no

## Prerequisiti

Livello 10 completato: lo starter parte dalla sua soluzione. Dopo il passo 1 ricostruisci l'immagine (`docker compose build`) per installare le nuove dipendenze.

## Cosa c'e' nello starter

Gia' pronti: tutto il codice dei livelli 01-10 e i test bersaglio (`tests/test_factories.py`, `tests/test_fixtures.py`, `tests/test_tooling.py`).

Da completare:

- `requirements-dev.txt`
- `palestra/tests/factories.py` (segnaposto che dicono quale passo manca)
- `palestra/tests/conftest.py` (le fixture del livello 11 sono segnaposto)
- `palestra/pytest.ini` e un nuovo `palestra/.coveragerc`
- `palestra/tests/test_policy_matrix.py` (per ora solo istruzioni)

## Cosa devi fare

1. **Dipendenze.** In `requirements-dev.txt` aggiungi `factory-boy` e `pytest-cov`.
2. **Factory** (`tests/factories.py`), tutte `factory.django.DjangoModelFactory`:
   - `UserFactory`: email unica con `factory.Sequence`, `name` con `factory.Faker`, password `password` impostata con `PostGenerationMethodCall('set_password', 'password')`;
   - `BoardFactory`: `title`, `owner = SubFactory(UserFactory)`, e un hook `post_generation` `with_places`: `BoardFactory(with_places=3)` crea anche tre luoghi;
   - `CollaboratorFactory`: `board` e `user` con `SubFactory`, ruolo `viewer`;
   - `PlaceFactory`: `name`, `lat` tra -90 e 90, `lng` tra -180 e 180, `board = SubFactory(BoardFactory)`;
   - `InboundAddressFactory`: `board = SubFactory(BoardFactory)`; il token lo genera gia' il modello.
3. **Fixture** (`tests/conftest.py`), costruite con le factory:
   - `owner` (`owner@example.com`) e `stranger` (`stranger@example.com`);
   - `board`: la bacheca `Roma` di `owner`;
   - `collaborator`: l'**utente** (non la riga `Collaborator`) con accesso in lettura a `board`;
   - `place`: `Colosseo` (41.8902, 12.4922) in `board`;
   - `owner_client`: il fixture `client` con `force_login(owner)`;
   - `api_client_owner`: un `APIClient` con `force_authenticate(user=owner)`.
4. **Copertura.**
   - In `pytest.ini`, dentro `addopts`: `--cov --cov-report=term-missing --cov-fail-under=80`.
   - Un `.coveragerc` accanto a `pytest.ini`: in `[run]` la `source` con `boards`, `places`, `inbox`, `core`, e un `omit` per `*/migrations/*` e `tests/*`.
5. **La matrice.** In `tests/test_policy_matrix.py` scrivi **un solo** test parametrizzato: quattro ruoli (`owner`, `collaborator`, `stranger`, `anonymous` con `AnonymousUser`) per tre azioni (`can_view_board`, `can_edit_board`, `can_add_collaborator`), cioe' almeno 12 casi, con id come `owner-view`. Usa le fixture del passo 3, niente `create_user`.
```bash
docker compose build
docker compose run --rm django pytest
docker compose run --rm django pytest tests/test_policy_matrix.py -v
docker compose run --rm django lint-imports
```

L'ultima riga dell'output di `pytest` e' il riepilogo della copertura: sotto l'80% il comando esce con errore anche se tutti i test passano.

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_factories.py` | ogni factory e' una `DjangoModelFactory` del modello giusto, email uniche, password cifrata, `build()` senza database, `SubFactory` sovrascrivibile, `with_places`, collaboratore che vede ma non modifica, coordinate valide, indirizzo inbound | **target dei TODO** (passi 1-2) |
| `tests/test_fixtures.py` | le fixture di `conftest.py`: utenti, bacheca, collaboratore, luogo, client con sessione, `APIClient` autenticato, isolamento tra test | **target dei TODO** (passo 3) |
| `tests/test_tooling.py` | `factory-boy` e `pytest-cov` nei requisiti, opzioni di copertura in `pytest.ini`, `source` e `omit` del `.coveragerc`, matrice parametrizzata con almeno 12 casi e tutti i ruoli, costruita con le fixture | **target dei TODO** (passi 1, 4, 5) |
| `tests/test_policy_matrix.py` | il tuo test parametrizzato (passo 5): sullo starter non contiene test | **scritto da te** |
| `tests/test_inbox.py` | livello 10 | **test di controllo** (regressione): passano gia' sullo starter |
| `tests/test_realtime.py` | livello 09 | **test di controllo** |
| `tests/test_celery_app.py`, `tests/test_geocode_task.py` | livello 08 | **test di controllo** |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

## Suggerimenti

- `build()` crea l'oggetto senza salvarlo: e' il modo piu' veloce quando il test non ha bisogno del database.
- Una fixture che chiede `db` (o un'altra fixture che lo chiede) ha accesso al database; non serve `@pytest.mark.django_db` dentro `conftest.py`.
- Con `factory_boy` recente, se usi `PostGenerationMethodCall` imposta `skip_postgeneration_save = True` in `Meta` e salva tu l'oggetto in un hook `post_generation`: cosi' non c'e' l'avviso di deprecazione.
- Una fixture di `conftest.py` vale per tutti i file di test; se un file definisce una fixture con lo stesso nome, vince quella del file.
- Gli id di `parametrize` (`ids=[...]` oppure `pytest.param(..., id='owner-view')`) compaiono nell'output: scegline di leggibili.
- La copertura misura le righe eseguite, non la qualita' dei test: l'80% e' un pavimento, non un traguardo. `term-missing` dice quali righe mancano.

## Prossimo livello

`12_teamwork/`: lavoro di squadra.
