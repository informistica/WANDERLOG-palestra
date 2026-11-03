"""Service layer dell'app places."""
from .models import Place


def add_place_to_board(board, name, lat, lng, description=""):
    """Aggiunge un luogo a una bacheca, validando bacheca e coordinate."""
    if board is None:
        raise ValueError("Serve una bacheca a cui aggiungere il luogo")
    lat, lng = float(lat), float(lng)
    if not -90 <= lat <= 90:
        raise ValueError("La latitudine deve essere tra -90 e 90")
    if not -180 <= lng <= 180:
        raise ValueError("La longitudine deve essere tra -180 e 180")
    return Place.objects.create(board=board, name=name, lat=lat, lng=lng,
                                description=description or "")


def place_to_feature(place):
    """Un luogo come Feature GeoJSON (RFC 7946).

    Attenzione all'ordine: in GeoJSON le coordinate sono [longitudine, latitudine].
    """
    # TODO (passo 1): un dizionario con type 'Feature', una geometry di tipo 'Point'
    #   e le properties id (come stringa), name, description
    raise NotImplementedError


def board_geojson(board):
    """I luoghi di `board` come FeatureCollection GeoJSON, in ordine di creazione."""
    # TODO (passo 1): type 'FeatureCollection' e una feature per ogni luogo della bacheca
    raise NotImplementedError
