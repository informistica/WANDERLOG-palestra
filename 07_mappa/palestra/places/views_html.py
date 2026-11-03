"""Pagina HTML della mappa di una bacheca (isola JavaScript con Leaflet)."""
from django.contrib.auth.decorators import login_required  # noqa: F401
from django.shortcuts import get_object_or_404, render  # noqa: F401
from django.urls import reverse  # noqa: F401

from boards.services import boards_visible_to  # noqa: F401


# TODO (passo 3): login obbligatorio
def board_map(request, board_pk):
    """La mappa dei luoghi: il JavaScript legge i dati dall'API GeoJSON."""
    # TODO (passo 3): bacheca visibile all'utente o 404; renderizza 'places/board_map.html'
    #   con board, geojson_url (reverse di 'board-map-geojson') e has_places
    raise NotImplementedError
