# Livello 10: Email in Entrata da Fixture .eml

## Obiettivo

Parsare email da fixture .eml, come WANDERLOG fa con conferme di prenotazione.

## Cosa si allena di WANDERLOG

- Parser email (§10)
- Fixture .eml (RES-03/04)
- Task 1A.6

## Prerequisiti

- Livello 09 completato
- Conoscenza email format

## Cosa devi fare

### Passo 1: Fixture .eml

Crea fixture email di esempio in tests/fixtures/

### Passo 2: Parser

Crea funzione che parsa .eml e estrae info

### Passo 3: Test

Test con fixture reali

### Passo 4: Verifica

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- Parser estrae info correttamente
- Fixture .eml valide
- Test passano

## Prossimo livello

Passa a `11_testing/`.
