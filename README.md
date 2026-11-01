# Palestra - Esercizi preparatori per WANDERLOG

Repository di esercizi per studenti di scuola superiore italiana che prepara, una competenza alla volta, per il progetto complesso Django **WANDERLOG** (clone di Wanderlog).

## Obiettivo

Questo repository contiene 12 livelli progressivi che introducono lo stack e le convenzioni usate nel progetto reale WANDERLOG:
- Django + Postgres in Docker Compose
- Regole strette di import tra app (lint-imports)
- Service layer
- Permessi proprietario/collaboratori
- API REST con Django REST Framework sotto `/api/v1/`
- Template Django + HTMX (no React, no build Node)
- Un'unica "isola" JavaScript con Leaflet per la mappa che legge GeoJSON
- Celery + Redis per task asincroni
- Channels per aggiornamenti real-time con frammenti HTML via estensione `ws` di HTMX
- Email in entrata parsate da fixture `.eml` (Mailpit in dev)
- pytest-django + factory_boy, copertura 80%
- Test e2e con Playwright
- CI con GitHub Actions
- django-allauth per autenticazione
- i18n it/en
- Lavoro di squadra con branch feat/*, PR e revisione incrociata

## Dominio mini: Bacheca dei Luoghi Preferiti

Invece del dominio completo di WANDERLOG (viaggi con collaboratori), usiamo un dominio molto più semplice:
una **bacheca di luoghi preferiti** con proprietario e collaboratori.

- **App `boards`**: la bacheca, il proprietario, i collaboratori, i permessi
- **App `places`**: i luoghi preferiti con dettagli e posizione
- **App `core`**: modello base, utilità comuni

## Struttura

Ogni livello è in una cartella numerata (`01_ambiente/`, `02_modelli/`, ecc.) ed è **auto-contenuto e eseguibile da solo**:
- Codice di partenza con TODO chiaramente marcati
- `README.md` con obiettivo, prerequisiti, quale parte di WANDERLOG prepara, istruzioni passo-passo, cosa consegnare, criteri di successo
- Test pre-scritti che **FALLISCONO** sul codice starter e **PASSANO** una volta completati i TODO (auto-verifica)

Ogni livello parte dallo stato completo del livello precedente, quindi i livelli successivi includono il lavoro già fatto.

## Come usare questo repository

1. **Scegli un livello** da cui partire (di solito si inizia da `01_ambiente/`)
2. **Leggi il README.md** nella cartella del livello
3. **Segui le istruzioni passo-passo**
4. **Completa i TODO** nel codice
5. **Esegui i test** per verificare il tuo lavoro:
   ```bash
   cd 01_ambiente/
   docker compose run --rm django pytest
   ```
6. **Quando tutti i test passano**, il livello è completo!

## Mappatura livelli → WANDERLOG

| Livello | Contenuto | Parte di WANDERLOG |
|---------|-----------|-------------------|
| 01 | Ambiente Docker Compose + Postgres | §9, §10, Task 0.1-0.2 |
| 02 | Modelli, migrazioni, admin Django | §5, Task 0.3 |
| 03 | Service layer e regole import | §6, lint-imports |
| 04 | Permessi proprietario/collaboratori | §7, policies |
| 05 | API REST con DRF | §11, Task 0.5 |
| 06 | Template Django + HTMX | §2, Task 0.9, D2 |
| 07 | Isola JavaScript: mappa Leaflet + GeoJSON | §2, Task 0.9, maps |
| 08 | Task asincroni Celery + Redis | §8, Task 0.4 |
| 09 | Tempo reale con Channels | §9, Task 0.6, 1A.5 |
| 10 | Email in entrata da fixture .eml | §10, RES-03/04 |
| 11 | Test completi: pytest, factory, coverage, CI | §11, Task 0.8 |
| 12 | Lavoro a coppie: branch, PR, review | §16, git workflow |

## Prerequisiti

- Docker e Docker Compose installati
- Git
- Editor di testo o IDE (VS Code, PyCharm, ecc.)
- Conoscenza base di:
  - Python
  - HTML/CSS
  - Git
  - Bash/terminale

## Versioni

Questo repository usa le stesse versioni di WANDERLOG:
- Python 3.12
- Django 5.2
- PostgreSQL 17
- Redis 7

## Workflow di verifica

Ogni livello include test che verificano automaticamente il completamento. Il workflow GitHub Actions esegue i test di tutti i livelli in parallelo, così l'insegnante può vedere quali livelli sono stati completati da ogni studente.

È normale che i livelli non ancora completati falliscano - il workflow è progettato per mostrare i progressi, non per bloccare.

## Supporto

Per domande o problemi:
1. Controlla il README.md del livello specifico
2. Rileggi le istruzioni passo-passo
3. Verifica che Docker sia in esecuzione
4. Chiedi all'insegnante

## Licenza

Materiale didattico per uso educativo.
