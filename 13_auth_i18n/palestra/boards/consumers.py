"""Consumer WebSocket delle bacheche: riceve soltanto (le scritture passano da HTTP)."""
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string

from .models import Board
from .policies import can_view_board
from .realtime import board_group

FORBIDDEN = 4403


class BoardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_pk']
        if not await self.board_visible():
            await self.close(code=FORBIDDEN)
            return
        self.group = board_group(self.board_id)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """Il WebSocket riceve soltanto: i messaggi del browser si ignorano."""

    async def board_event(self, event):
        # I permessi possono cambiare a connessione aperta: si ricontrollano a ogni evento
        if not await self.board_visible():
            await self.close(code=FORBIDDEN)
            return
        html = render_to_string('boards/_place_oob.html', {'place': event['payload']['place']})
        await self.send(text_data=html)

    @database_sync_to_async
    def board_visible(self):
        board = Board.objects.filter(pk=self.board_id).first()
        return board is not None and can_view_board(self.scope.get('user'), board)
