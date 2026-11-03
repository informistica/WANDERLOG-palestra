# Livello 12: lavorare in squadra

## Obiettivo

Wanderlog funziona e ha 289 test. Adesso deve poterci lavorare un team senza rompere `main`. Ogni modifica passa da un branch `feat/...`, una **Pull Request** con template e review, un controllo automatico prima del commit (**pre-commit** con **ruff**) e una **CI su GitHub Actions** che ripete tutto su Postgres e Redis veri: ruff, `lint-imports`, migrazioni, `pytest` con la soglia di copertura del livello 11.

## Cosa si allena di WANDERLOG

- Flusso di lavoro con branch `feat/*` e `fix/*`, Pull Request, review, **Squash and merge**
- `CONTRIBUTING.md` e `.github/pull_request_template.md`
- `ruff` configurato in `ruff.toml` (regole, `line-length`, esclusioni, `per-file-ignores`)
- `pre-commit`: `.pre-commit-config.yaml`, `rev` fissata, `pre-commit install`, `pre-commit run --all-files`
- GitHub Actions: trigger `push`/`pull_request`, `services` Postgres e Redis con health check, `env`, `working-directory`, ordine degli step

## Prerequisiti

Livello 11 completato: lo starter parte dalla sua soluzione. Ti servono un account GitHub e un tuo repository (anche privato) in cui copiare il progetto.

## Cosa c'e' nello starter

Gia' pronti: tutto il codice dei livelli 01-11 e il test bersaglio `tests/test_teamwork.py`.

Da completare (tutti nella root del livello, accanto a `requirements-dev.txt`):

- `CONTRIBUTING.md` (solo istruzioni)
- `.github/pull_request_template.md` (solo istruzioni)
- `requirements-dev.txt`
- `.github/workflows/ci.yml` (YAML valido ma quasi vuoto)
- due file nuovi: `ruff.toml` e `.pre-commit-config.yaml`

## Cosa devi fare

1. **Il flusso del team** (`CONTRIBUTING.md`). Spiega, in italiano e senza lasciare `TODO`:
   - nomi dei branch: `feat/<cosa>`, `fix/<cosa>`, creati da `main` aggiornato;
   - `pre-commit install` prima del primo commit;
   - i controlli prima della PR: `ruff check .`, `lint-imports`, `pytest`;
   - Pull Request verso `main`, CI verde, almeno una review approvata, poi merge.
2. **Template delle PR** (`.github/pull_request_template.md`): sezioni "Cosa cambia" e "Come verificarla", poi una checklist di almeno 3 caselle `- [ ]` che citi `pytest`, `lint-imports` e le migrazioni.
3. **Ruff e pre-commit.**
   - In `requirements-dev.txt` aggiungi `ruff` e `pre-commit`.
   - `ruff.toml`: `line-length = 100`, in `[lint]` le regole `select = ["E4", "E7", "E9", "F"]`, le migrazioni escluse con `extend-exclude`. Se ruff segnala problemi nel codice esistente, correggili o, solo se hai un buon motivo, usa `[lint.per-file-ignores]`.
   - `.pre-commit-config.yaml`: il repo `https://github.com/astral-sh/ruff-pre-commit` con una `rev` fissa (`v0.17.3`) e l'hook `ruff-check`; il repo `https://github.com/pre-commit/pre-commit-hooks` con `check-yaml` e `detect-private-key`.
4. **La CI** (`.github/workflows/ci.yml`):
   - parte su `push` e `pull_request` verso `main`;
   - `services` `postgres:17` e `redis:7`, ognuno con `--health-cmd`;
   - nell'`env` del job: `DJANGO_SECRET_KEY`, `DATABASE_URL` (postgres su `localhost`), `REDIS_URL`, `CELERY_BROKER_URL` e le altre variabili di `.env.example`;
   - step in ordine: `actions/checkout`, `actions/setup-python` con `python-version: '3.12'`, `pip install -r requirements-dev.txt`, creazione del `.env`, `ruff check .`, poi in `palestra/` (`working-directory: palestra`) `lint-imports` e `pytest` con la soglia di copertura.
5. **Provalo davvero.** Crea un tuo repository con il contenuto di questa cartella nella root (compreso il .gitignore, che tiene fuori .env): GitHub esegue solo i workflow in `<root del repo>/.github/workflows`, quindi quello che sta in `12_teamwork/.github` qui nella palestra non parte. Poi:
   ```bash
   git switch -c feat/teamwork
   pre-commit install
   pre-commit run --all-files
   git add . && git commit -m "Aggiungi CI e regole del team"
   git push -u origin feat/teamwork
   ```
   Apri la Pull Request, guarda la CI nella scheda **Checks** e, se puoi, fatti fare la review da un compagno. In **Settings > Branches** puoi proteggere `main`: PR obbligatoria e CI verde prima del merge.

```bash
docker compose build
docker compose run --rm django pytest tests/test_teamwork.py -v
docker compose run --rm django pytest
docker compose run --rm django lint-imports
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_teamwork.py` | il workflow e' YAML valido: trigger, servizi con health check, variabili, Python 3.12, step ruff / `lint-imports` / `pytest` con soglia nell'ordine giusto e in `palestra/`; `.pre-commit-config.yaml` con ruff e hook generici; `ruff.toml` valido e `ruff check` pulito sul progetto; `ruff` e `pre-commit` nei requisiti; template PR con checklist; `CONTRIBUTING.md` con branch, PR, review e comandi | **target dei TODO** (passi 1-4) |
| `tests/test_factories.py`, `tests/test_fixtures.py`, `tests/test_tooling.py`, `tests/test_policy_matrix.py` | livello 11 | **test di controllo** (regressione): passano gia' sullo starter |
| `tests/test_inbox.py` | livello 10 | **test di controllo** |
| `tests/test_realtime.py` | livello 09 | **test di controllo** |
| `tests/test_celery_app.py`, `tests/test_geocode_task.py` | livello 08 | **test di controllo** |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

I test bersaglio leggono i file, non eseguono GitHub Actions: la prova che la CI funziona e' il segno verde sulla tua Pull Request.

## Facoltativo: smoke test nel browser con Playwright

Non c'e' un test automatico per questo passo (un browser in CI e' lento e fragile). Se vuoi provarlo:

```bash
pip install pytest-playwright
playwright install chromium
```

Scrivi un test che apre la pagina di login con il fixture `live_server` di pytest-django, entra con un utente creato dalla factory e controlla che la lista delle bacheche si veda. Tienilo in un file separato con un marker (`@pytest.mark.e2e`) e lancialo a parte: `pytest -m e2e`.

## Suggerimenti

- PyYAML legge la chiave `on:` come il booleano `True` (YAML 1.1). GitHub la capisce comunque; i test controllano entrambe le forme.
- `pre-commit run --all-files` la prima volta scarica gli hook: serve la rete. Dopo, `git commit` controlla solo i file modificati.
- `ruff check --fix` corregge da solo import inutilizzati e simili; rileggi sempre il diff.
- Un servizio senza health check fa partire i test prima che Postgres accetti connessioni: errori a caso nel primo step.
- La soglia `--cov-fail-under=80` sta gia' in `pytest.ini` dal livello 11; ripeterla nel workflow la rende visibile a chi legge la CI.
- Non mettere segreti veri nel workflow: per la CI basta una chiave finta. Quelli veri vanno in **Settings > Secrets and variables > Actions** e si leggono con `${{ secrets.NOME }}`.

## Fine della palestra

Hai finito i 12 livelli. Il prossimo passo e' WANDERLOG vero: le stesse regole, su un progetto tuo.