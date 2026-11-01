# Livello 04: Sistema di Permessi Proprietario/Collaboratori

## Obiettivo

Implementare un sistema di permessi che distingue tra proprietario e collaboratori di una board, come il sistema di permessi di WANDERLOG per i viaggi.

## Cosa si allena di WANDERLOG

- Matrice dei permessi (§7 del piano)
- Sistema di collaboratori e ruoli
- Policy centralizzate per controllo accessi
- Pattern usato in `trips/policies.py` di WANDERLOG

## Prerequisiti

- Livello 03 completato
- Comprensione di permessi e autorizzazioni
- Conoscenza di query Django

## Sistema di Permessi

Una Board può avere:
- Un **proprietario** (owner): può fare tutto
- **Collaboratori** (viewers): possono solo leggere

## Cosa devi fare

### Passo 1: Aggiungi modello Collaborator

In `boards/models.py`, crea il modello `Collaborator`:
- FK a `Board`
- FK a `User`  
- Campo `role` con scelte: `viewer` (default)
- Constraint unique su (board, user)

### Passo 2: Crea policies.py

Crea `boards/policies.py` con le funzioni:
- `can_view_board(user, board)`: True se user è owner o collaborator
- `can_edit_board(user, board)`: True solo se user è owner
- `can_add_collaborator(user, board)`: True solo se user è owner

### Passo 3: Aggiorna i service

In `boards/services.py`, aggiungi:
- `add_collaborator(board, user, role='viewer')`: aggiunge un collaborator
- Valida con `can_add_collaborator` prima di aggiungere

### Passo 4: Registra Collaborator nell'admin

In `boards/admin.py`, registra il modello `Collaborator`.

### Passo 5: Crea e applica migrazione

```bash
docker compose exec django python manage.py makemigrations
docker compose exec django python manage.py migrate
```

### Passo 6: Verifica con i test

```bash
docker compose run --rm django pytest
```

## Cosa consegnare

- Modello `Collaborator` implementato
- File `boards/policies.py` con le 3 funzioni
- Service `add_collaborator` implementato
- Migrazioni create e applicate
- Collaborator registrato nell'admin
- Test passati

## Criteri di successo

- Il proprietario può visualizzare e modificare la board
- I collaboratori possono solo visualizzare
- Solo il proprietario può aggiungere collaboratori
- `can_view_board`, `can_edit_board`, `can_add_collaborator` funzionano correttamente
- Tutti i test passano

## Suggerimenti

- Usa `exists()` per controlli efficienti su Collaborator
- Le policy sono funzioni pure che ricevono user e board
- Nessun controllo di autenticazione qui (user è già autenticato)

## Prossimo livello

Passa a `05_api/` per creare l'API REST.
