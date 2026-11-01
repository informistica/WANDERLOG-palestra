"""Policy per il controllo accessi alle board."""


def can_view_board(user, board):
    """
    TODO: Implementa il controllo se un utente può visualizzare una board.
    
    Args:
        user: L'utente da verificare
        board: La board da verificare
    
    Returns:
        bool: True se l'utente è owner o collaborator
    """
    # TODO: Ritorna True se:
    # - user è il proprietario (board.owner == user)
    # - oppure user è un collaborator (esiste un Collaborator con board=board e user=user)
    # Usa board.collaborators.filter(user=user).exists() per il secondo check
    pass


def can_edit_board(user, board):
    """
    TODO: Implementa il controllo se un utente può modificare una board.
    
    Args:
        user: L'utente da verificare
        board: La board da verificare
    
    Returns:
        bool: True solo se l'utente è owner
    """
    # TODO: Ritorna True solo se user è il proprietario
    pass


def can_add_collaborator(user, board):
    """
    TODO: Implementa il controllo se un utente può aggiungere collaboratori.
    
    Args:
        user: L'utente da verificare
        board: La board da verificare
    
    Returns:
        bool: True solo se l'utente è owner
    """
    # TODO: Ritorna True solo se user è il proprietario
    # (stessa logica di can_edit_board)
    pass
