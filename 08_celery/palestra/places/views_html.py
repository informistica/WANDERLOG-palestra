"""Pagina HTML della mappa di una bacheca (isola JavaScript con Leaflet)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from boards.services import boards_visible_to


@login_required
def board_map(request, board_pk):
    """La mappa dei luoghi: il JavaScript legge i dati dall'API GeoJSON."""
    board = get_object_or_404(boards_visible_to(request.user), pk=board_pk)
    return render(request, 'places/board_map.html', {
        'board': board,
        'geojson_url': reverse('board-map-geojson', kwargs={'board_pk': board.pk}),
        'has_places': board.places.exists(),
    })
