"""Service layer dell'app boards: l'unico punto in cui si creano bacheche e collaborazioni."""
from django.db.models import Q

from .models import Board, Collaborator
from .policies import can_add_collaborator, can_edit_board


def boards_visible_to(user):
    """Bacheche che `user` può vedere: le sue e quelle in cui è collaboratore."""
    if user is None or not user.is_authenticated:
        return Board.objects.none()
    return Board.objects.filter(Q(owner=user) | Q(collaborators__user=user)).distinct()


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


def update_board(board, title, description="", *, requesting_user):
    """Modifica titolo e descrizione di `board` per conto di `requesting_user`.

    Solleva PermissionError se l'utente non può modificarla, ValueError se il titolo è vuoto.
    """
    # TODO (passo 4): stesso schema di add_collaborator: prima la policy
    #   (can_edit_board), poi la validazione del titolo (strip, non vuoto), poi il salvataggio
    raise NotImplementedError
