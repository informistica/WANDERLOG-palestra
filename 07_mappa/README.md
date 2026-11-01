# Livello 07: Isola JavaScript con Mappa Leaflet

## Obiettivo

Creare un'isola JavaScript con Leaflet per visualizzare luoghi su mappa, leggendo GeoJSON dall'API.

## Cosa si allena di WANDERLOG

- Isola JavaScript (§2)
- Leaflet + GeoJSON
- Task 0.9
- Unica isola JS nell'app

## Prerequisiti

- Livello 06 completato
- JavaScript base
- Familiarità con mappe

## Cosa devi fare

### Passo 1: Download Leaflet

Scarica leaflet.js e leaflet.css in `places/static/places/`

### Passo 2: Template mappa

Crea template con div per la mappa

### Passo 3: Script JavaScript

Crea script che carica places e li mostra su mappa Leaflet

### Passo 4: Endpoint GeoJSON

API che ritorna places come GeoJSON FeatureCollection

### Passo 5: Test

```bash
docker compose run --rm django pytest
```

## Criteri di successo

- Mappa Leaflet si carica
- Places mostrati come marker
- GeoJSON corretto
- Test passano

## Prossimo livello

Passa a `08_celery/`.
