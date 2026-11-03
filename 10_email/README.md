# Livello 10: luoghi inviati per email

## Obiettivo

Ogni bacheca ha un indirizzo email, `board+<token>@palestra.local`. Chi inoltra a quell'indirizzo un link di Google Maps trova il luogo sulla bacheca e riceve una ricevuta. In sviluppo la posta in uscita non parte davvero: finisce in **Mailpit**, che la mostra su http://localhost:8025.

## Cosa si allena di WANDERLOG

- Una nuova app, `inbox`, sopra `places` nei layer di `lint-imports` (`inbox -> places -> boards -> core`)
- Leggere un'email vera con la libreria standard: `email.message_from_bytes(..., policy=policy.default)`, intestazioni codificate (RFC 2047), corpo in base64, parti HTML
- Una corrispondenza indirizzo -> bacheca con un token difficile da indovinare (`InboundAddress`)
- Le **policy** del livello 04 anche qui: il mittente deve poter vedere la bacheca (proprietario o collaboratore)
- Ogni email resta tracciata (`InboundEmail`) con l'esito: `parsed`, `unrecognized`, `rejected`
- Idempotenza con il `Message-ID`: la stessa email consegnata due volte non crea due luoghi
- La ricevuta con un task Celery accodato con `transaction.on_commit` (livello 08), mai a chi e' stato scartato (niente *backscatter*)
- Un comando di gestione, `python manage.py ingest_eml`
- Le email nei test: backend `locmem` e `django.core.mail.outbox`

## Prerequisiti

Livello 09 completato: lo starter parte dalla sua soluzione. Aggiungi al tuo `.env` le variabili email di `.env.example` (`EMAIL_HOST`, `EMAIL_PORT`, `DEFAULT_FROM_EMAIL`, `INBOUND_EMAIL_DOMAIN`). Le fixture `.eml` usano il dominio `palestra.local`: lascia quel valore.

## Cosa c'e' nello starter

Gia' pronti:

- l'app `inbox` in `INSTALLED_APPS`, con `models.py`, la migrazione `0001_initial` e l'admin
- `.importlinter` con il nuovo layer (e `tests/test_architecture.py` aggiornato di conseguenza)
- `.env.example` con le variabili email
- le email di prova in `tests/fixtures/emails/`

Da completare:

- `palestra/settings.py`
- `compose.yaml`
- `inbox/services.py`
- `inbox/tasks.py`
- `inbox/management/commands/ingest_eml.py`

## Cosa devi fare

1. **Impostazioni e Mailpit.**
   - In `settings.py`: `EMAIL_BACKEND` SMTP, `EMAIL_HOST` (default `mailpit`), `EMAIL_PORT` (default 1025, intero), `DEFAULT_FROM_EMAIL` (default `noreply@palestra.local`), `INBOUND_EMAIL_DOMAIN` (default `palestra.local`), tutti dalle variabili d'ambiente.
   - In `compose.yaml`: un servizio `mailpit` con l'immagine `axllent/mailpit`, le porte `8025:8025` (web) e `1025:1025` (SMTP); `django` e `celery-worker` dipendono da `mailpit`.
2. **Indirizzi** (`inbox/services.py`).
   - `address_for_board(board)`: `get_or_create` dell'`InboundAddress`, poi `board+<token>@<INBOUND_EMAIL_DOMAIN>`.
   - `board_from_recipient(address)`: accetta anche `Nome <indirizzo>`, ignora le maiuscole, restituisce la bacheca oppure `None`.
3. **Coordinate.** `parse_coordinates(text)` riconosce `@lat,lng` (i link `google.com/maps/place/...`), `?q=lat,lng` e `query=lat%2Clng`, `geo:lat,lng`. Restituisce `(lat, lng)` oppure `None`, e scarta i valori fuori scala.
4. **L'email** (`ingest_eml(raw)`), dentro una transazione:
   - `Message-ID` gia' visto: restituisci l'`InboundEmail` che esiste;
   - nessun destinatario (`To` o `Cc`) e' una bacheca: `rejected`;
   - il mittente non e' un utente che puo' vedere la bacheca: `rejected`;
   - nessuna coordinata nell'oggetto o nel corpo (testo, oppure HTML se manca): `unrecognized`;
   - altrimenti `add_place_to_board`, con il nome preso dall'oggetto senza `Fwd:`, `I:`, `R:`: `parsed`.
5. **La ricevuta** (`inbox/tasks.py`). Per `parsed` e `unrecognized`, con `transaction.on_commit`, accoda `send_ingest_receipt.delay(str(record.id))`. Il task restituisce `missing`, `skipped` (scartate) o `sent`; l'oggetto e' `Luogo aggiunto: <nome>` oppure `Email non riconosciuta`, con l'invito a inoltrare un link di Google Maps.
6. **Il comando.** `ingest_eml file.eml [altro.eml ...]`: una riga per file, `<file>: <status>`; un file che non si legge e' un `CommandError`.

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose up
```

Per provare a mano:

1. In `python manage.py shell`: `from inbox.services import address_for_board`, poi l'indirizzo di una tua bacheca.
2. Copia una fixture, metti quell'indirizzo nel `To:` e il tuo utente nel `From:`.
3. `docker compose run --rm django python manage.py ingest_eml percorso/del/file.eml`
4. Il luogo e' sulla bacheca; la ricevuta e' su http://localhost:8025 (serve `celery-worker` acceso).

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_inbox.py` | impostazioni dall'ambiente, Mailpit nel compose, indirizzo della bacheca e lettura del destinatario, coordinate dai link, email del proprietario e del collaboratore (in Cc, in HTML), oggetto codificato e corpo base64, mittente in maiuscolo e link `geo:`, mittenti e indirizzi scartati, email senza coordinate, Message-ID ripetuto, ricevuta solo dopo il commit, aiuto per le email non riconosciute, nessuna risposta agli scartati, comando `ingest_eml` | **target dei TODO** (passi 1-6) |
| `tests/test_realtime.py` | livello 09 | **test di controllo** (regressione): passano gia' sullo starter |
| `tests/test_celery_app.py`, `tests/test_geocode_task.py` | livello 08 | **test di controllo** |
| `tests/test_map_geojson.py`, `tests/test_map_page.py` | livello 07 | **test di controllo** |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 (layer aggiornati con `inbox`) | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

## Suggerimenti

- Con `policy.default` le intestazioni arrivano gia' decodificate (`=?utf-8?q?...?=` diventa `Caffè`) e `get_body(preferencelist=('plain', 'html'))` sceglie la parte giusta; `get_content()` decodifica il base64.
- `email.utils.getaddresses` separa una lista di destinatari; `parseaddr` toglie il nome visualizzato.
- `@` compare anche negli indirizzi email: l'espressione deve volere due numeri separati da una virgola subito dopo.
- **Attenzione al `From:`**: chiunque puo' scrivere il mittente che vuole. Qui la protezione e' il token segreto dell'indirizzo; in produzione si controllano anche SPF, DKIM e DMARC (o si lasciano al servizio che riceve la posta, come Mailgun o SES).
- `inbox` puo' importare `places` e `boards`, non il contrario.
- Nei test pytest-django usa il backend `locmem`: le email finiscono in `mail.outbox`, non in Mailpit.

## Prossimo livello

`11_testing/`: factory_boy, fixture condivise e soglia di copertura.