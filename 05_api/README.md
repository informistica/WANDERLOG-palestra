# Livello 05: API REST con Django REST Framework

## Obiettivo

Creare un'API REST completa per boards e places usando Django REST Framework, come l'API /api/v1/ di WANDERLOG.

## Cosa si allena di WANDERLOG

- API REST con DRF (§11)
- Serializers
- ViewSets
- Routing /api/v1/
- Task 0.5

## Prerequisiti

- Livello 04 completato
- Conoscenza di REST API
- Familiarità con JSON

## Cosa devi fare

### Passo 1: Installa DRF

Aggiungi a `requirements.txt`:
```
djangorestframework>=3.15
```

### Passo 2: Configura DRF

In `settings.py`, aggiungi 'rest_framework' a INSTALLED_APPS e configura:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

### Passo 3: Crea serializers

- `boards/serializers.py` con BoardSerializer e CollaboratorSerializer
- `places/serializers.py` con PlaceSerializer

### Passo 4: Crea ViewSets

- `boards/views.py` con BoardViewSet
- `places/views.py` con PlaceViewSet

### Passo 5: Configura URL

Crea `palestra/urls.py` con router DRF sotto `/api/v1/`

### Passo 6: Test

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- GET /api/v1/boards/ lista le boards
- POST /api/v1/boards/ crea una board
- GET /api/v1/places/ lista i places
- Serializers funzionano correttamente
- Tutti i test passano

## Prossimo livello

Passa a `06_htmx/`.
