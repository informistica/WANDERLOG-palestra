"""Service layer dell'app places."""
from .models import Place


def add_place_to_board(board, name, lat, lng, description=""):
    """Aggiunge un luogo a una bacheca, validando bacheca e coordinate.

    Raises:
        ValueError: se board è None o le coordinate sono fuori intervallo
    """
    # TODO: se board è None solleva ValueError
    # TODO: lat deve stare tra -90 e 90, lng tra -180 e 180 (altrimenti ValueError)
    # TODO: crea e restituisci il Place
    raise NotImplementedError
