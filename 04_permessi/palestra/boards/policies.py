"""Policy di accesso alle bacheche: funzioni pure, restituiscono True/False.

Un utente anonimo (AnonymousUser o None) non può mai nulla:
controlla user is not None e user.is_authenticated.
"""


def can_view_board(user, board):
    """True se user è il proprietario o un collaboratore della bacheca."""
    # TODO: proprietario (board.owner_id == user.pk)
    # TODO: oppure collaboratore: board.collaborators.filter(user=user).exists()
    raise NotImplementedError


def can_edit_board(user, board):
    """True solo per il proprietario."""
    # TODO
    raise NotImplementedError


def can_add_collaborator(user, board):
    """True solo per il proprietario."""
    # TODO
    raise NotImplementedError
