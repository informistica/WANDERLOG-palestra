# Livello 05: API REST con Django REST Framework

## Obiettivo

Esporre bacheche, collaboratori e luoghi con un'API REST sotto `/api/v1/`, riusando le policy e i servizi dei livelli 03-04. È lo schema di WANDERLOG (§4 e §7 del piano): una sola API versionata, sessione di Django, accesso solo autenticato, permessi decisi dalle policy.

## Cosa si allena di WANDERLOG

- Configurazione DRF centralizzata in `REST_FRAMEWORK` (autenticazione a sessione, `IsAuthenticated` di default, paginazione comune)
- Permission class DRF che chiamano le stesse policy usate dai servizi (`boards/policies.py`)
- Chi non può vedere una risorsa riceve **404** (non si rivela che esiste); chi la vede ma non può modificarla riceve **403**
- Le scritture passano dai servizi (`create_board`, `add_collaborator`, `add_place_to_board`), non da `serializer.save()` sparsi nelle view
- URL annidati con il router DRF di base (`boards/{board_pk}/places/`)
- `places` usa `boards`, mai il contrario (contratto `lint-imports`)

## Prerequisiti

Livello 04 completato: lo starter parte dalla sua soluzione. `djangorestframework` è già in `requirements.txt`: ricostruisci l'immagine con `docker compose build`.

## Cosa c'è nello starter

- `palestra/settings.py`: `rest_framework` e `REST_FRAMEWORK` da aggiungere
- `core/pagination.py`: `DefaultPagination` da completare
- `boards/services.py`: `boards_visible_to` da implementare
- `boards/permissions.py`: `BoardPolicy` da implementare
- `boards/serializers.py`, `places/serializers.py`: campi da completare
- `boards/views.py`: `BoardViewSet` e l'azione `collaborators` da scrivere
- `places/views.py`: `BoardPlaceViewSet` da completare
- `palestra/urls.py`: router da registrare sotto `/api/v1/`

## Cosa devi fare

1. **Configurazione.** Aggiungi `'rest_framework'` a `INSTALLED_APPS` e configura `REST_FRAMEWORK`: `SessionAuthentication`, `IsAuthenticated`, `DEFAULT_PAGINATION_CLASS = 'core.pagination.DefaultPagination'`, `PAGE_SIZE = 20`. In `core/pagination.py`: `page_size = 20`, `page_size_query_param = 'page_size'`, `max_page_size = 100`.
2. **Servizio di lettura.** `boards_visible_to(user)` restituisce le bacheche di cui `user` è proprietario o collaboratore, senza duplicati; per `None` o un utente anonimo restituisce un queryset vuoto.
3. **Permission class.** `BoardPolicy.has_object_permission`: per i metodi sicuri (`GET`, `HEAD`, `OPTIONS`) usa `can_view_board`, per gli altri `can_edit_board`.
4. **Serializer.**
   - `BoardSerializer`: `id`, `title`, `description`, `owner` (email, sola lettura), `created_at`, `updated_at`;
   - `CollaboratorSerializer`: `id`, `user` (email), `role`, `created_at`;
   - `PlaceSerializer`: `id`, `board` (sola lettura), `name`, `description`, `lat`, `lng`, `created_at`.
5. **`BoardViewSet`** (`/api/v1/boards/`):
   - `get_queryset` usa `boards_visible_to`, così chi non vede la bacheca riceve 404;
   - `perform_create` crea con `create_board(request.user, ...)`; un `ValueError` diventa 400;
   - azione `POST /api/v1/boards/{id}/collaborators/` che chiama `add_collaborator(..., requesting_user=request.user)`: `PermissionError` → 403, `ValueError` → 400, successo → 201.
6. **`BoardPlaceViewSet`** (`/api/v1/boards/{board_pk}/places/`): lista, dettaglio, creazione, cancellazione.
   - la bacheca dell'URL deve essere visibile (altrimenti 404);
   - creare e cancellare richiede `can_edit_board` (altrimenti 403);
   - la creazione passa da `add_place_to_board`; coordinate non valide → 400;
   - la bacheca arriva dall'URL, non dal corpo della richiesta.
7. **URL.** In `palestra/urls.py` registra i due viewset su un `DefaultRouter` e includilo sotto `api/v1/`.

```bash
docker compose build
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose run --rm django python manage.py makemigrations --check
```

Per provare a mano: entra nell'admin (`/admin/`) e poi apri `http://localhost:8000/api/v1/boards/` nel browser; l'API navigabile di DRF usa la stessa sessione.

## Matrice dei permessi

| Chi | Leggere | Modificare / cancellare | Aggiungere collaboratori o luoghi |
|---|---|---|---|
| Anonimo | 403 | 403 | 403 |
| Estraneo | 404 | 404 | 404 |
| Collaboratore (`viewer`) | 200 | 403 | 403 |
| Proprietario | 200 | 200 / 204 | 201 |

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_api.py` | configurazione DRF, `boards_visible_to`, login obbligatorio, bacheche e collaboratori via API | **target dei TODO** (passi 1-5, 7) |
| `tests/test_api_places.py` | luoghi via API: lettura, scrittura, matrice dei permessi | **target dei TODO** (passi 4, 6, 7) |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** (regressione): passano già sullo starter |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

Questo livello non cambia i modelli: `makemigrations --check` deve continuare a non trovare nulla.

## Suggerimenti

- Il 404 per gli estranei viene gratis se `get_queryset` filtra già le bacheche visibili: `get_object()` non le trova.
- `get_object()` chiama `has_object_permission` solo sulle bacheche visibili: lì il "no" diventa 403.
- Nell'azione `collaborators` imposta `permission_classes=[IsAuthenticated]`: il permesso lo decide il servizio, non `BoardPolicy`.
- In `perform_create` assegna `serializer.instance = create_board(...)`: DRF usa `serializer.data` per la risposta 201.
- Per il 404 su un `board_pk` non valido usa `rest_framework.generics.get_object_or_404`, che gestisce anche gli UUID malformati.

## Prossimo livello

`06_templates_htmx/`: viste HTML con template e HTMX sopra gli stessi servizi.
