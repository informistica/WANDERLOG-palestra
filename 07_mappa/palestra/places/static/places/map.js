// Isola JavaScript della mappa (livello 07): niente build, un file statico servito da Django.
// Legge i luoghi dall'API GeoJSON indicata in data-geojson-url, con la sessione dell'utente.
(function () {
  'use strict';

  var ITALIA = [41.9, 12.5];

  // TODO (passo 5): il contenuto del popup come elemento DOM: il nome in grassetto e,
  //   se c'e', la descrizione. Assegna i testi con textContent: arrivano dagli utenti.
  function popupContent(props) {
    return document.createElement('div');
  }

  function init(el) {
    // TODO (passo 5):
    //   1. crea la mappa Leaflet sull'elemento el, centrata su ITALIA con zoom 5;
    //   2. scarica il GeoJSON dall'URL del data attribute (dataset), con la sessione;
    //   3. aggiungi i luoghi con il layer GeoJSON di Leaflet, un popup per ciascuno;
    //   4. se ci sono luoghi adatta la vista ai loro confini;
    //   5. se la richiesta fallisce mostra un messaggio sotto la mappa.
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-geojson-url]').forEach(init);
  });
})();
