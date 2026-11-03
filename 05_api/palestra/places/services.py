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
