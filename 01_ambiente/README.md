# Livello 01: Ambiente Docker Compose + Postgres

## Obiettivo

Imparare a configurare un ambiente di sviluppo Django con Docker Compose e PostgreSQL, come in WANDERLOG.

## Cosa si allena di WANDERLOG

- Configurazione Docker Compose (§9 del piano di implementazione)
- Variabili d'ambiente (§10)
- Task 0.1 e 0.2 del piano

## Prerequisiti

- Docker e Docker Compose installati
- Conoscenza base di Python e Django
- Editor di testo

## Cosa c'è nello starter

- `compose.yaml` parzialmente completo con TODO
- `Dockerfile` con TODO
- `.env.example` da copiare in `.env`
- `requirements.txt` di base
- Struttura minimal Django in `palestra/`
- Test che verificano l'ambiente

## Cosa devi fare

### Passo 1: Copia le variabili d'ambiente

```bash
cp .env.example .env
```

Genera una `DJANGO_SECRET_KEY` sicura e inseriscila in `.env`. Puoi usare:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Passo 2: Completa il Dockerfile

Apri `Dockerfile` e:
1. Trova i TODO
2. Installa le dipendenze Python (`requirements.txt`)
3. Copia il codice del progetto nel container

### Passo 3: Completa compose.yaml

Apri `compose.yaml` e:
1. Trova i TODO
2. Configura il servizio Django per usare `.env`
3. Configura il healthcheck di Postgres
4. Aggiungi `depends_on` con condizione `service_healthy` per il database

### Passo 4: Verifica con i test

Costruisci e avvia i servizi:

```bash
docker compose build
docker compose up -d
```

Esegui i test:

```bash
docker compose run --rm django pytest
```

## Cosa consegnare

- `.env` con una `DJANGO_SECRET_KEY` valida (NON committare questo file!)
- `Dockerfile` completo
- `compose.yaml` completo
- Screenshot o output del comando `docker compose ps` che mostra i servizi in esecuzione
- Output dei test passati

## Criteri di successo

✅ `docker compose build` completa senza errori
✅ `docker compose up -d` avvia tutti i servizi
✅ `docker compose ps` mostra `django`, `db`, e `redis` in stato `running`
✅ Il database passa il healthcheck
✅ `docker compose run --rm django pytest` esegue e passa tutti i test
✅ `docker compose exec django python manage.py check` non mostra errori

## Suggerimenti

- Il healthcheck di Postgres usa `pg_isready -U user -d palestra_db`
- Il servizio Django deve attendere che il database sia healthy prima di partire
- Se i container non partono, controlla i log con `docker compose logs`
- Il file `.env` NON deve essere committato su git (è già in `.gitignore`)

## Prossimo livello

Una volta completato questo livello, passa a `02_modelli/` dove creerai i modelli Django per Board e Place.
