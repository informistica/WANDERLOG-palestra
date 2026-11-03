// Isola JavaScript della mappa (livello 07): niente build, un file statico servito da Django.
// Legge i luoghi dall'API GeoJSON indicata in data-geojson-url, con la sessione dell'utente.
(function () {
  'use strict';

  var ITALIA = [41.9, 12.5];

  function popupContent(props) {
    // Solo textContent: nome e descrizione sono scritti dagli utenti.
    var box = document.createElement('div');
    var title = document.createElement('strong');
    title.textContent = props.name;
    box.appendChild(title);
    if (props.description) {
      var text = document.createElement('p');
      text.textContent = props.description;
      box.appendChild(text);
    }
    return box;
  }

  function init(el) {
    var map = L.map(el).setView(ITALIA, 5);
    fetch(el.dataset.geojsonUrl, {
      credentials: 'same-origin',
      headers: { Accept: 'application/json' }
    })
      .then(function (response) {
        if (!response.ok) { throw new Error('HTTP ' + response.status); }
        return response.json();
      })
      .then(function (data) {
        var layer = L.geoJSON(data, {
          onEachFeature: function (feature, marker) {
            marker.bindPopup(popupContent(feature.properties));
          }
        }).addTo(map);
        if (data.features.length) {
          map.fitBounds(layer.getBounds(), { padding: [24, 24], maxZoom: 15 });
        }
      })
      .catch(function () {
        var msg = document.createElement('p');
        msg.setAttribute('role', 'alert');
        msg.textContent = 'Impossibile caricare i luoghi della mappa.';
        el.after(msg);
      });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-geojson-url]').forEach(init);
  });
})();
