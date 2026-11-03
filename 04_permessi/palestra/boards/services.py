"""Service layer dell'app boards: l'unico punto in cui si creano bacheche e collaborazioni."""
from .models import Board, Collaborator
from .policies import can_add_collaborator


def create_board(owner, title, description=""):
    """Crea una bacheca di `owner`. Solleva ValueError se il titolo è vuoto."""
    title = (title or "").strip()
    if not title:
        raise ValueError("Il titolo della bacheca è obbligatorio")
    return Board.objects.create(owner=owner, title=title, description=description or "")


def add_collaborator(board, user, role=Collaborator.ROLE_VIEWER, *, requesting_user):
    """Condivide `board` con `user`. Solo il proprietario può farlo."""
    # TODO: PermissionError se requesting_user non può aggiungere collaboratori (usa la policy)
    # TODO: ValueError("Il proprietario non può essere ...") se user è il proprietario
    # TODO: ValueError se user è già collaboratore
    # TODO: crea e restituisci il Collaborator
    raise NotImplementedError
