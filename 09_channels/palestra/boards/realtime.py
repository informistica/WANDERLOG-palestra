"""Eventi in tempo reale delle bacheche: il gruppo Channels e l'invio di un evento."""
from asgiref.sync import async_to_sync  # noqa: F401
from channels.layers import get_channel_layer  # noqa: F401


def board_group(board_id):
    """Nome del gruppo Channels di una bacheca."""
    # TODO (passo 2): 'board_' seguito dall'id
    raise NotImplementedError


def broadcast_board_event(board_id, payload):
    """Invia `payload` a tutti i WebSocket aperti sulla bacheca (codice sincrono)."""
    # TODO (passo 2): group_send al gruppo della bacheca di un messaggio
    #   {'type': 'board.event', 'payload': payload}; group_send e' asincrona
    raise NotImplementedError
