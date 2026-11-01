# Livello 09: Tempo Reale con Django Channels

## Obiettivo

Implementare aggiornamenti real-time con Django Channels e WebSocket, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- Channels (§9)
- WebSocket
- Task 1A.5
- ASGI

## Prerequisiti

- Livello 08 completato
- Conoscenza WebSocket base

## Cosa devi fare

### Passo 1: Installa Channels

Aggiungi channels, channels-redis, daphne a requirements

### Passo 2: Configura ASGI

Aggiorna asgi.py con ProtocolTypeRouter

### Passo 3: Consumer

Crea consumer per board updates

### Passo 4: Routing

Configura routing WebSocket

### Passo 5: Test

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- WebSocket si connette
- Messaggi real-time funzionano
- Consumer funziona
- Test passano

## Prossimo livello

Passa a `10_email/`.
