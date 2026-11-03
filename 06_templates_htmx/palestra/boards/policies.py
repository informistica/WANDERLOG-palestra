"""Policy di accesso alle bacheche: funzioni pure, restituiscono True/False."""


def _is_authenticated(user):
    return user is not None and getattr(user, 'is_authenticated', False)


def can_view_board(user, board):
    """Proprietario o collaboratore."""
    if not _is_authenticated(user):
        return False
    return board.owner_id == user.pk or board.collaborators.filter(user=user).exists()


def can_edit_board(user, board):
    """Solo il proprietario."""
    return _is_authenticated(user) and board.owner_id == user.pk


def can_add_collaborator(user, board):
    """Solo il proprietario."""
    return can_edit_board(user, board)
