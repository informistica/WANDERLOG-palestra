# Livello 02: Modelli, Migrazioni e Admin

## Obiettivo

Imparare a definire modelli Django con UUID come chiave primaria, creare migrazioni, e configurare l'interfaccia di amministrazione, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- Modello dati (§5 del piano di implementazione)
- `BaseModel` con UUID e timestamp
- Custom User model con email come USERNAME_FIELD
- Migrazioni (Task 0.3)
- Django Admin

## Prerequisiti

- Livello 01 completato
- Conoscenza dei modelli Django
- Comprensione delle migrazioni

## Cosa c'è nello starter

Partendo dal Livello 01 completo, vengono aggiunti:
- App `core`, `boards`, `places` create ma vuote
- `Dockerfile` e `compose.yaml` completi (dal Livello 01)
- Modelli con TODO da completare
- Test che verificano la struttura dei modelli

## Cosa devi fare

### Passo 1: Completa il Dockerfile e compose.yaml

Copia le soluzioni dal Livello 01 (o completa i TODO se non l'hai già fatto):

**Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gettext && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/palestra

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

**compose.yaml:**
```yaml
services:
  django:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    working_dir: /app/palestra
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: python manage.py runserver 0.0.0.0:8000

  db:
    image: postgres:17
    environment:
      POSTGRES_DB: palestra_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d palestra_db"]
      interval: 5s
      retries: 10

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Passo 2: Completa BaseModel in core/models.py

Il `BaseModel` è un modello astratto con:
- `id` come UUID (chiave primaria)
- `created_at` e `updated_at` con timestamp automatici

### Passo 3: Completa User in boards/models.py

Il modello `User` deve:
- Ereditare da `AbstractUser`
- Usare `id` UUID come chiave primaria
- Usare `email` come `USERNAME_FIELD` (no username)
- Avere i campi: `name`, `language` (default 'it')

### Passo 4: Completa Board e Place

**Board** (in `boards/models.py`):
- Eredita da `BaseModel`
- Campi: `title`, `description`, `owner` (FK a User)
- `__str__` ritorna il title

**Place** (in `places/models.py`):
- Eredita da `BaseModel`  
- Campi: `name`, `lat`, `lng`, `description`, `board` (FK a Board)
- `__str__` ritorna il name

### Passo 5: Configura INSTALLED_APPS

In `settings.py`, aggiungi le app nell'ordine corretto:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'boards',
    'places',
]
```

E imposta:
```python
AUTH_USER_MODEL = 'boards.User'
```

### Passo 6: Crea le migrazioni

```bash
# Rimuovi il vecchio database se esiste
docker compose down -v

# Ricostruisci e avvia
docker compose up -d --build

# Crea le migrazioni
docker compose exec django python manage.py makemigrations

# Applica le migrazioni
docker compose exec django python manage.py migrate
```

### Passo 7: Registra i modelli nell'admin

In `boards/admin.py` e `places/admin.py`, registra i modelli.

### Passo 8: Verifica con i test

```bash
docker compose run --rm django pytest
```

## Cosa consegnare

- Modelli completati in `core/models.py`, `boards/models.py`, `places/models.py`
- File di migrazione generati
- Admin registrati
- Output dei test passati
- Screenshot dell'admin Django con almeno un Board e un Place creati

## Criteri di successo

✅ `makemigrations` genera le migrazioni iniziali per boards e places
✅ `migrate` applica tutte le migrazioni senza errori
✅ `makemigrations --check --dry-run` non trova nuove migrazioni
✅ Tutti i test passano
✅ L'admin Django permette di creare User, Board e Place
✅ Il modello User usa UUID come pk
✅ Il modello User usa email come USERNAME_FIELD (no username)

## Suggerimenti

- Per UUID: `import uuid` e `models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`
- Per User senza username: `username = None` e custom manager
- I timestamp automatici: `auto_now_add=True` per created_at, `auto_now=True` per updated_at
- Ricorda `python manage.py createsuperuser` per accedere all'admin

## Prossimo livello

Una volta completato, passa a `03_servizi/` dove imparerai il service layer e le regole di import.
