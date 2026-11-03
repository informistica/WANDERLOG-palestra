"""Consumer WebSocket delle bacheche: riceve soltanto (le scritture passano da HTTP)."""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string  # noqa: F401

from .models import Board  # noqa: F401
from .policies import can_view_board  # noqa: F401
from .realtime import board_group  # noqa: F401

FORBIDDEN = 4403


class BoardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # TODO (passo 3): prendi board_pk da self.scope['url_route']['kwargs'];
        #   se la bacheca non e' visibile chiudi con codice FORBIDDEN;
        #   altrimenti entra nel gruppo della bacheca e accetta
        raise NotImplementedError

    async def disconnect(self, code):
        # TODO (passo 3): esci dal gruppo (se ci eri entrato)
        pass

    async def receive(self, text_data=None, bytes_data=None):
        """Il WebSocket riceve soltanto: i messaggi del browser si ignorano."""

    async def board_event(self, event):
        # TODO (passo 3): ricontrolla la visibilita' (chiudi con FORBIDDEN se non c'e' piu'),
        #   poi manda al browser boards/_place_oob.html con event['payload']['place']
        raise NotImplementedError

    @database_sync_to_async
    def board_visible(self):
        # TODO (passo 3): la bacheca esiste ed e' visibile a self.scope['user'] (can_view_board)
        raise NotImplementedError
