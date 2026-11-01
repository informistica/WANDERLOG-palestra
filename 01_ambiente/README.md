# Livello 01: ambiente con Docker Compose e Postgres

## Obiettivo

Configurare l'ambiente di sviluppo come in WANDERLOG: Django in un container, PostgreSQL 17 e Redis 7 come servizi del compose, le variabili in `.env`.

## Cosa si allena di WANDERLOG

- §9 del piano (compose: `env_file: .env`, healthcheck di `db`, `depends_on`)
- §10 (variabili d'ambiente, `.env.example`)
- Task 0.1 e 0.2 (ambiente, dipendenze e immagine)

## Prerequisiti

- Docker Desktop (o Docker Engine con il plugin compose)
- Python e Django di base

## Cosa c'è nello starter

- `Dockerfile` con TODO
- `compose.yaml` con TODO
- `.env.example` da copiare in `.env`
- `requirements.txt` e `requirements-dev.txt`
- un progetto Django minimo in `palestra/` (`settings.py` legge già le variabili d'ambiente)
- i test in `palestra/tests/`

## Cosa devi fare

### Passo 1: le variabili d'ambiente

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Metti la chiave generata in `DJANGO_SECRET_KEY` dentro `.env`. Il file `.env` non va mai committato (è già nel `.gitignore`).

### Passo 2: il Dockerfile

Completa i TODO:
1. immagine base `python:3.12-slim`;
2. copia `requirements.txt` e `requirements-dev.txt` e installa `requirements-dev.txt` con `pip` (prima del codice, così Docker riusa la cache quando cambi solo il codice);
3. copia il resto del progetto con `COPY . .`.

### Passo 3: compose.yaml

Completa i TODO:
1. il servizio `django` legge `.env` con `env_file`;
2. `depends_on`: `db` con `condition: service_healthy`, `redis` con `condition: service_started`;
3. il healthcheck di `db` con `pg_isready -U user -d palestra_db`.

### Passo 4: verifica

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose run --rm django pytest
```

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_docker_config.py` | i TODO del `Dockerfile` e di `compose.yaml` | **target dei TODO**: falliscono sullo starter |
| `tests/test_environment.py` | `.env` presente, `DJANGO_SECRET_KEY` valida, connessione a Postgres e Redis, `manage.py check` | **test di controllo**: dipendono dal tuo `.env` e dai servizi avviati, non dal codice dei TODO. Se l'ambiente è a posto passano anche sullo starter |

## Criteri di successo

- `docker compose build` e `docker compose up -d` terminano senza errori
- `docker compose ps` mostra `django`, `db` (healthy) e `redis` in esecuzione
- `docker compose run --rm django pytest` passa tutti i test

## Suggerimenti

- Se un container non parte: `docker compose logs django`
- Il servizio `django` parte solo quando `db` è healthy: se resta in attesa, controlla il healthcheck

## Prossimo livello

`02_modelli/`: custom user, `Board` e `Place`.
