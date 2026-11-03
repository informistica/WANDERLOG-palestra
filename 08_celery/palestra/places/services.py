"""Service layer dell'app places."""
from django.db import transaction  # noqa: F401

from .models import Place
from .tasks import geocode_place  # noqa: F401


def add_place_to_board(board, name, lat, lng, description=""):
    """Aggiunge un luogo a una bacheca, validando bacheca e coordinate."""
    if board is None:
        raise ValueError("Serve una bacheca a cui aggiungere il luogo")
    lat, lng = float(lat), float(lng)
    if not -90 <= lat <= 90:
        raise ValueError("La latitudine deve essere tra -90 e 90")
    if not -180 <= lng <= 180:
        raise ValueError("La longitudine deve essere tra -180 e 180")
    place = Place.objects.create(board=board, name=name, lat=lat, lng=lng,
                                 description=description or "")
    # TODO (passo 4): accoda geocode_place con l'id del luogo, ma solo dopo il commit
    #   della transazione (transaction.on_commit)
    return place


def place_to_feature(place):
    """Un luogo come Feature GeoJSON (RFC 7946).

    Attenzione all'ordine: in GeoJSON le coordinate sono [longitudine, latitudine].
    """
    return {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [place.lng, place.lat]},
        'properties': {
            'id': str(place.id),
            'name': place.name,
            'description': place.description,
        },
    }


def board_geojson(board):
    """I luoghi di `board` come FeatureCollection GeoJSON, in ordine di creazione."""
    places = Place.objects.filter(board=board).order_by('created_at')
    return {'type': 'FeatureCollection', 'features': [place_to_feature(p) for p in places]}
