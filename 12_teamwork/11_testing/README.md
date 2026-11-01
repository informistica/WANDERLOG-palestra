# Livello 11: Suite Test Completa con Coverage

## Obiettivo

Implementare suite test completa con pytest, factory_boy, coverage 80%, come WANDERLOG.

## Cosa si allena di WANDERLOG

- pytest-django (§11)
- factory_boy
- coverage 80%
- Task 0.8
- GitHub Actions CI

## Prerequisiti

- Livello 10 completato
- Conoscenza pytest

## Cosa devi fare

### Passo 1: Factory Boy

Crea factories per User, Board, Place

### Passo 2: Coverage

Configura coverage e raggiungi 80%

### Passo 3: CI

Verifica che CI passa

### Passo 4: Test

```bash
docker compose run --rm django pytest --cov
```

## Criteri di successo

- Coverage >= 80%
- Factory funzionano
- CI passa
- Tutti test passano

## Prossimo livello

Passa a `12_teamwork/`.
