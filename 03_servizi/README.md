# Livello 03: Service Layer e Regole di Import

## Obiettivo

Implementare un service layer per separare la logica di business dai modelli e configurare lint-imports per prevenire dipendenze circolari tra app, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- Service layer pattern (§6 del piano)
- Grafo delle dipendenze tra app (§6)
- `lint-imports` per controllo automatico (§6)
- Regole: un'app può importare solo app di livello inferiore

## Prerequisiti

- Livello 02 completato
- Comprensione del concetto of separation of concerns
- Conoscenza di base delle dipendenze tra moduli

## Struttura delle Dipendenze

```
places → boards → core
```

## Cosa devi fare

### Passo 1: Installa import-linter

Aggiungi a `requirements-dev.txt`:
```
import-linter>=2.0
```

### Passo 2: Crea `.importlinter`

Nella cartella `palestra/` (accanto a `manage.py`)

### Passo 3: Crea services.py

In `boards/services.py` e `places/services.py`

### Passo 4: Test

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
```

## Criteri di successo

- `lint-imports` esegue senza errori
- Service creano correttamente oggetti
- Tutti i test passano

## Prossimo livello

Passa a `04_permessi/`.
