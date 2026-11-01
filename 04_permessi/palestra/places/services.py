"""Service layer per l'app places."""
from .models import Place


def add_place_to_board(board, name, lat, lng, description=""):
    """
    TODO: Implementa l'aggiunta di un luogo a una board.
    
    Args:
        board: La board a cui aggiungere il luogo
        name: Nome del luogo
        lat: Latitudine
        lng: Longitudine
        description: Descrizione (opzionale)
    
    Returns:
        Place: Il luogo creato
        
    Raises:
        ValueError: Se board è None
    """
    # TODO: Valida che board non sia None (raise ValueError se lo è)
    # TODO: Crea e ritorna un Place con i parametri forniti
    pass
