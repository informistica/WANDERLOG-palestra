"""Service layer dell'app boards: l'unico punto in cui si creano le bacheche."""
from .models import Board


def create_board(owner, title, description=""):
    """Crea una bacheca di `owner`. Solleva ValueError se il titolo è vuoto.

    Returns:
        Board: la bacheca creata
    """
    # TODO: togli gli spazi in testa e in coda a title
    # TODO: se il titolo è vuoto solleva ValueError
    # TODO: crea e restituisci la Board
    raise NotImplementedError
