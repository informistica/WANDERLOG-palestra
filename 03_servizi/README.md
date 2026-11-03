# Livello 03: service layer e regole di import

## Obiettivo

Spostare la logica di scrittura in funzioni di servizio (`services.py`) e far controllare a `lint-imports` il grafo delle dipendenze tra app, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- §6 del piano: service layer, grafo delle dipendenze tra app, `lint-imports` in CI
- Regola: un'app importa solo app dei livelli sotto di lei

```
places  →  boards  →  core
```

`places` può importare `boards` e `core`; `boards` solo `core`; `core` nessuna app del progetto.

## Prerequisiti

Livello 02 completato: lo starter parte dalla sua soluzione (modelli e migrazioni pronti).

## Cosa c'è nello starter

- `boards/services.py` e `places/services.py` con le funzioni da scrivere
- `palestra/.importlinter` con i pacchetti radice ma senza contratto
- `import-linter` è già in `requirements-dev.txt` (ricostruisci l'immagine: `docker compose build`)

## Cosa devi fare

1. `boards/services.py`, `create_board(owner, title, description="")`: toglie gli spazi in testa e in coda al titolo, solleva `ValueError` se il titolo è vuoto, crea e restituisce la `Board`.
2. `places/services.py`, `add_place_to_board(board, name, lat, lng, description="")`: solleva `ValueError` se `board` è `None`, se `lat` non è tra -90 e 90 o `lng` non è tra -180 e 180; crea e restituisce il `Place`.
3. `palestra/.importlinter`: aggiungi un contratto `type = layers` con i livelli `places`, `boards`, `core` (dall'alto verso il basso).

```bash
docker compose run --rm django lint-imports
docker compose run --rm django pytest
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_services.py` | i due servizi e le loro validazioni | **target dei TODO** (passi 1-2) |
| `tests/test_architecture.py` | il contratto di `.importlinter` e l'esito di `lint-imports` | **target dei TODO** (passo 3) |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py`, `tests/test_environment.py`, `tests/test_docker_config.py` | livelli 01-02 | **test di controllo** (regressione): passano già sullo starter |

## Criteri di successo

- `lint-imports` riporta `1 kept, 0 broken`
- tutti i test passano

## Suggerimenti

- Prova a rompere la regola: aggiungi `import places` in `boards/services.py` e rilancia `lint-imports`. Poi togli l'import.
- Le view e l'API dei prossimi livelli chiameranno questi servizi: niente `objects.create` sparsi nel codice.

## Prossimo livello

`04_permessi/`: collaboratori e policy.
