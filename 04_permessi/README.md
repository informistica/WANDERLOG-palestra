# Livello 04: collaboratori e policy

## Obiettivo

Condividere una bacheca con altri utenti e decidere chi può fare cosa con **policy**: funzioni pure che rispondono "sì/no", chiamate da servizi, view e API. È lo schema owner/collaborator di WANDERLOG (§7 del piano).

## Cosa si allena di WANDERLOG

- Modello di collaborazione con vincolo di unicità
- Policy in un modulo dedicato (`boards/policies.py`), usate dai servizi
- I servizi rifiutano le operazioni non permesse con `PermissionError`

## Prerequisiti

Livello 03 completato: lo starter parte dalla sua soluzione.

## Cosa c'è nello starter

- `boards/models.py`: `Collaborator` con i campi da scrivere
- `boards/policies.py`: tre policy da implementare
- `boards/services.py`: `add_collaborator` da implementare
- `boards/admin.py`: `Collaborator` da registrare

## Cosa devi fare

1. `Collaborator`: `board` (`related_name='collaborators'`), `user` (`related_name='collaborations'`), `role` con `choices=ROLE_CHOICES` e default `viewer`, `unique_together` su `(board, user)`. Poi `makemigrations boards`.
2. `boards/policies.py`:
   - `can_view_board(user, board)`: proprietario o collaboratore;
   - `can_edit_board(user, board)`: solo il proprietario;
   - `can_add_collaborator(user, board)`: solo il proprietario.
   Un utente anonimo (o `None`) non può mai nulla.
3. `add_collaborator(board, user, role='viewer', *, requesting_user)`:
   - `PermissionError` se `requesting_user` non può aggiungere collaboratori;
   - `ValueError` con la parola "proprietario" se `user` è il proprietario;
   - `ValueError` se `user` è già collaboratore;
   - altrimenti crea e restituisce il `Collaborator`.
4. Registra `Collaborator` nell'admin.

```bash
docker compose run --rm django python manage.py makemigrations boards
docker compose run --rm django pytest
docker compose run --rm django lint-imports
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_permissions.py` | modello, policy, servizio `add_collaborator` | **target dei TODO** (passi 1-3) |
| `tests/test_policies_edge.py` | utenti anonimi, collaboratore duplicato, admin di `Collaborator` | **target dei TODO** (passi 2-4) |
| `tests/test_migrations.py` | migrazioni iniziali presenti e allineate ai modelli | `test_initial_migration_exists`: **test di controllo**; `test_no_missing_migrations`: **target dei TODO**, fallisce finché non crei la migrazione di `Collaborator` (passo 1) |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_services.py`, `tests/test_architecture.py`, `tests/test_environment.py`, `tests/test_docker_config.py` | livelli 01-03 | **test di controllo** (regressione): passano già sullo starter |

## Suggerimenti

- `board.collaborators.filter(user=user).exists()` evita di caricare tutti i collaboratori.
- Le policy non sollevano eccezioni: restituiscono `True`/`False`. È il servizio a trasformare un "no" in `PermissionError`.

## Prossimo livello

`05_api/`: API REST con Django REST Framework.
