"""Eventi in tempo reale delle bacheche: il gruppo Channels e l'invio di un evento."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def board_group(board_id):
    """Nome del gruppo Channels di una bacheca."""
    return f'board_{board_id}'


def broadcast_board_event(board_id, payload):
    """Invia `payload` a tutti i WebSocket aperti sulla bacheca (codice sincrono)."""
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(board_group(board_id), {'type': 'board.event', 'payload': payload})
