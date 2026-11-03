# Livello 07: la mappa dei luoghi

## Obiettivo

Mostrare i luoghi di una bacheca su una mappa interattiva. È l'unico punto di WANDERLOG con JavaScript scritto a mano (§2 del piano e decisione #65): una piccola **isola** che vive solo nella pagina della mappa e legge i dati da un endpoint dell'API in formato GeoJSON, con la sessione e le solite policy.

## Cosa si allena di WANDERLOG

- La libreria della mappa (Leaflet 1.9.4) **vendorizzata** in `places/static/places/leaflet/`: file statici versionati nel repository, niente CDN, niente Node, niente build
- CSS e JS di Leaflet caricati **solo** nella pagina della mappa, tramite i blocchi `head` e `scripts` di `base.html`
- Un endpoint `GET /api/v1/boards/{id}/map/` che restituisce una `FeatureCollection` GeoJSON (RFC 7946), con le coordinate in ordine **[longitudine, latitudine]**
- Le stesse regole del resto dell'API: login obbligatorio, estraneo **404**, collaboratore in lettura
- La trasformazione dei modelli in GeoJSON in un servizio (`places/services.py`), non nella view
- Un'isola JavaScript che riceve l'URL dei dati da un attributo `data-` del template, invece di avere URL scritti nel codice
- Popup costruiti con `textContent`: nome e descrizione li scrivono gli utenti, `innerHTML` aprirebbe la porta all'XSS

In WANDERLOG l'isola sta nell'app `maps` e mostra i luoghi di un viaggio; qui il suo ruolo lo fa l'app `places`, con i luoghi di una bacheca. Come nel piano con il provider finto (decisione #66), la mappa **non ha uno sfondo a tasselli**: solo i segnaposto. Le tile arriveranno con un provider vero.

## Prerequisiti

Livello 06 completato: lo starter parte dalla sua soluzione. Nessun pacchetto Python nuovo: non serve ricostruire l'immagine.

## Cosa c'è nello starter

Già pronti:

- `places/static/places/leaflet/`: Leaflet 1.9.4 (`leaflet.js`, `leaflet.css`, `images/`, `LICENSE`), preso dal pacchetto npm `leaflet` e controllato con il suo hash `sha512` (file di terze parti: non va modificato)
- `core/templates/base.html`: i blocchi vuoti `{% block head %}` e `{% block scripts %}`
- `palestra/urls.py`: la rotta `api/v1/boards/<id>/map/` (nome `board-map-geojson`) e le pagine di `places/urls.py` sotto `/boards/`
- `places/urls.py`: la rotta `/boards/<id>/mappa/` (nome `places:board-map`)
- `boards/templates/boards/board_detail.html`: il link "Vedi sulla mappa"

Da completare:

- `places/services.py`: `place_to_feature` e `board_geojson`
- `places/views.py`: `BoardMapView.get`
- `places/views_html.py`: `board_map`
- `places/templates/places/board_map.html`: il CSS, il contenitore della mappa, il messaggio per la bacheca vuota, gli script
- `places/static/places/map.js`: l'isola

## L'endpoint e la pagina

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [12.4922, 41.8902]},
      "properties": {"id": "…uuid…", "name": "Colosseo", "description": "Anfiteatro Flavio"}
    }
  ]
}
```

| Chi | `GET /api/v1/boards/<id>/map/` | `GET /boards/<id>/mappa/` |
|---|---|---|
| Anonimo | 403 | redirect al login |
| Estraneo | 404 (JSON) | 404 |
| Collaboratore (`viewer`) | 200 | 200 |
| Proprietario | 200 | 200 |

## Cosa devi fare

1. **Servizi GeoJSON.** `place_to_feature(place)` restituisce una `Feature` con geometria `Point` e coordinate `[place.lng, place.lat]` (numeri, non stringhe) e le `properties` `id` (stringa), `name`, `description`. `board_geojson(board)` restituisce la `FeatureCollection` con i luoghi della bacheca in ordine di creazione; per una bacheca vuota `features` è `[]`.
2. **L'API.** In `BoardMapView.get` prendi la bacheca con `get_object_or_404(boards_visible_to(request.user), pk=board_pk)`, come fa `BoardPlaceViewSet.get_board`, e rispondi `Response(board_geojson(board))`.
3. **La view della pagina.** `board_map` con `@login_required`; stessa ricerca della bacheca (404 agli estranei); renderizza `places/board_map.html` con `board`, `geojson_url` (`reverse('board-map-geojson', kwargs={'board_pk': board.pk})`) e `has_places`.
4. **Il template.**
   - nel blocco `head`: `<link rel="stylesheet" href="{% static 'places/leaflet/leaflet.css' %}">`;
   - `<div id="board-map" data-geojson-url="{{ geojson_url }}" role="region" aria-label="…" style="height: 28rem"></div>`: senza altezza Leaflet disegna una mappa alta zero;
   - `<p id="mappa-vuota">Nessun luogo da mostrare sulla mappa.</p>`, con l'attributo `hidden` se `has_places`;
   - nel blocco `scripts`: prima `places/leaflet/leaflet.js`, poi `places/map.js`, entrambi con `defer` (così vengono eseguiti in quest'ordine, a pagina letta).
5. **L'isola `map.js`.**
   - `L.map(el)` sul contenitore, centrata sull'Italia;
   - `fetch(el.dataset.geojsonUrl, {credentials: 'same-origin', headers: {Accept: 'application/json'}})`;
   - `L.geoJSON(data, {onEachFeature: …})` con `marker.bindPopup(popupContent(feature.properties))`;
   - se ci sono luoghi, `map.fitBounds(layer.getBounds(), {padding: [24, 24], maxZoom: 15})`: con un solo luogo `maxZoom` evita lo zoom al massimo;
   - in `popupContent` crea gli elementi con `document.createElement` e assegna i testi con `textContent`;
   - nel `.catch` mostra un messaggio sotto la mappa.

```bash
docker compose run --rm django pytest
docker compose run --rm django lint-imports
docker compose run --rm django python manage.py makemigrations --check
docker compose up
```

Per provare a mano: aggiungi due o tre luoghi a una bacheca dall'admin o dall'API, apri `http://localhost:8000/boards/<id>/mappa/` e clicca un segnaposto. Nella scheda Rete del browser vedi la richiesta a `/api/v1/boards/<id>/map/`; nelle altre pagine Leaflet non viene caricato.

## I test

| File | Cosa verifica | Tipo |
|---|---|---|
| `tests/test_map_geojson.py` | servizi GeoJSON, forma della `FeatureCollection`, ordine `[lng, lat]`, `properties`, solo i luoghi della bacheca, bacheca vuota, permessi dell'endpoint | **target dei TODO** (passi 1-2) |
| `tests/test_map_page.py` | login, contenitore con `data-geojson-url`, link dal dettaglio, permessi, Leaflet solo nella pagina della mappa, messaggio per la bacheca vuota, file statici e isola `map.js` | **target dei TODO** (passi 3-5) |
| `tests/test_htmx_base.py`, `tests/test_board_pages.py` | livello 06 | **test di controllo** (regressione): passano già sullo starter |
| `tests/test_api.py`, `tests/test_api_places.py` | livello 05 | **test di controllo** |
| `tests/test_permissions.py`, `tests/test_policies_edge.py` | livello 04 | **test di controllo** |
| `tests/test_services.py`, `tests/test_architecture.py` | livello 03 | **test di controllo** |
| `tests/test_models.py`, `tests/test_admin.py`, `tests/test_migrations.py` | livello 02 | **test di controllo** |
| `tests/test_environment.py`, `tests/test_docker_config.py` | livello 01 | **test di controllo** |

I test non aprono un browser: controllano l'HTML, l'API e il sorgente di `map.js`. Il comportamento dell'isola lo verifichi a mano nella pagina. Questo livello non cambia i modelli: `makemigrations --check` deve continuare a non trovare nulla.

## Suggerimenti

- L'ordine delle coordinate è l'errore più comune: GeoJSON vuole `[lng, lat]`, mentre Leaflet, quando gli passi coordinate a mano (`setView`), vuole `[lat, lng]`. `L.geoJSON` fa la conversione da solo.
- La richiesta anonima all'API riceve 403 già da DRF (`IsAuthenticated` nelle impostazioni): per questo il test del login controlla anche che il proprietario riceva 200.
- La view HTML importa `boards.services`: `places` può usare `boards`, il contratto `lint-imports` resta rispettato.
- Per avere uno sfondo puoi aggiungere, solo in locale, `L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap'})`: l'attribuzione è obbligatoria. In WANDERLOG le tile arrivano con il provider vero.

## Prossimo livello

`08_celery/`: lavori in background con Celery e Redis.
