# Livello 08: Task Asincroni con Celery

## Obiettivo

Implementare task asincroni con Celery + Redis, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- Celery + Redis (§8)
- Task asincroni
- Task 0.4
- Beat per task periodici

## Prerequisiti

- Livello 07 completato
- Conoscenza di task asincroni

## Cosa devi fare

### Passo 1: Configura Celery

Crea `palestra/celery.py` con configurazione base

### Passo 2: Task di esempio

Crea task che invia email di benvenuto

### Passo 3: Worker in compose

Aggiungi servizio celery-worker al compose.yaml

### Passo 4: Test

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- Celery configurato
- Task eseguono correttamente
- Worker funziona
- Test passano

## Prossimo livello

Passa a `09_channels/`.
