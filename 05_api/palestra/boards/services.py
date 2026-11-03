"""Service layer dell'app boards: l'unico punto in cui si creano bacheche e collaborazioni."""
from django.db.models import Q  # noqa: F401  (ti servirà per boards_visible_to)

from .models import Board, Collaborator
from .policies import can_add_collaborator


def boards_visible_to(user):
    """Bacheche che `user` può vedere: le sue e quelle in cui è collaboratore."""
    # TODO (passo 2): utente None o anonimo -> Board.objects.none()
    # TODO (passo 2): proprietario OPPURE collaboratore: combina due condizioni con Q e |
    #   (il related_name verso Collaborator è 'collaborators')
    #   Attenzione: il JOIN sui collaboratori duplica le righe -> .distinct()
    raise NotImplementedError


def create_board(owner, title, description=""):
    """Crea una bacheca di `owner`. Solleva ValueError se il titolo è vuoto."""
    title = (title or "").strip()
    if not title:
        raise ValueError("Il titolo della bacheca è obbligatorio")
    return Board.objects.create(owner=owner, title=title, description=description or "")


def add_collaborator(board, user, role=Collaborator.ROLE_VIEWER, *, requesting_user):
    """Condivide `board` con `user`. Solo il proprietario può farlo."""
    if not can_add_collaborator(requesting_user, board):
        raise PermissionError("Solo il proprietario può aggiungere collaboratori")
    if board.owner_id == user.pk:
        raise ValueError("Il proprietario non può essere aggiunto come collaboratore")
    if board.collaborators.filter(user=user).exists():
        raise ValueError("L'utente è già collaboratore della bacheca")
    return Collaborator.objects.create(board=board, user=user, role=role)
