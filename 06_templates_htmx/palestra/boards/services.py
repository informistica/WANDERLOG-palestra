"""Service layer per l'app boards."""
from .models import Board, Collaborator
from .policies import can_add_collaborator


def create_board(owner, title, description=""):
    board = Board.objects.create(
        owner=owner,
        title=title,
        description=description
    )
    return board


def add_collaborator(board, user, role='viewer', requesting_user=None):
    """TODO: Aggiungi un collaborator a una board."""
    # TODO: Se requesting_user è fornito, verifica con can_add_collaborator
    # TODO: Se user è l'owner, raise ValueError("Il proprietario non può essere collaborator")
    # TODO: Crea e ritorna Collaborator
    pass
