"""Livello 09: Channels, il consumer della bacheca e la diffusione degli eventi.

Niente pytest-asyncio (decisione #25 di WANDERLOG): ogni test e' sincrono e fa girare
uno scenario asincrono con async_to_sync. Il consumer legge il database con
database_sync_to_async, che chiude le connessioni vecchie: per questo i test che lo
usano hanno transaction=True.
"""
import os

import pytest
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.test import Client, TestCase

from boards import realtime
from boards.models import Board, Collaborator
from places import services as place_services
from places.services import add_place_to_board

User = get_user_model()
TIMEOUT = 3


@pytest.fixture
def people(db):
    owner = User.objects.create_user(email='owner@example.com', password='test12345')
    viewer = User.objects.create_user(email='viewer@example.com', password='test12345')
    stranger = User.objects.create_user(email='stranger@example.com', password='test12345')
    return owner, viewer, stranger


@pytest.fixture
def board(people):
    owner, viewer, _ = people
    board = Board.objects.create(title='Roma', owner=owner)
    Collaborator.objects.create(board=board, user=viewer)
    return board


def ws_app():
    from boards.routing import websocket_urlpatterns
    return URLRouter(websocket_urlpatterns)


def communicator(board_id, user=None):
    comm = WebsocketCommunicator(ws_app(), f'/ws/boards/{board_id}/')
    if user is not None:
        comm.scope['user'] = user
    return comm


def place_event(name='Colosseo', place_id='p1'):
    return {'event': 'place.added', 'place': {'id': place_id, 'name': name}}


class TestSettings:
    """Passo 1."""

    def test_asgi_settings(self):
        assert settings.INSTALLED_APPS[0] == 'daphne', 'daphne va per primo (sostituisce runserver)'
        assert settings.ASGI_APPLICATION == 'palestra.asgi.application'

    def test_redis_channel_layer(self):
        layer_conf = settings.CHANNEL_LAYERS['default']
        assert layer_conf['BACKEND'] == 'channels_redis.core.RedisChannelLayer'
        assert layer_conf['CONFIG']['hosts'] == [os.environ['CHANNEL_LAYER_URL']]

        async def roundtrip():
            from channels.layers import get_channel_layer
            layer = get_channel_layer()
            channel = await layer.new_channel()
            await layer.group_add('palestra_test', channel)
            await layer.group_send('palestra_test', {'type': 'prova', 'n': 1})
            message = await layer.receive(channel)
            await layer.group_discard('palestra_test', channel)
            return message

        assert async_to_sync(roundtrip)() == {'type': 'prova', 'n': 1}


class TestBroadcast:
    """Passo 2: gruppo e invio, chiamati dal service layer dopo il commit."""

    def test_board_group(self):
        assert realtime.board_group('abc') == 'board_abc'

    def test_broadcast_reaches_group(self, inmemory_channel_layer):
        layer = inmemory_channel_layer

        async def scenario():
            channel = await layer.new_channel()
            await layer.group_add('board_42', channel)
            await sync_to_async(realtime.broadcast_board_event)(42, place_event())
            return await layer.receive(channel)

        assert async_to_sync(scenario)() == {'type': 'board.event', 'payload': place_event()}

    @pytest.mark.django_db
    def test_service_broadcasts_after_commit(self, board, monkeypatch):
        sent = []
        monkeypatch.setattr(place_services, 'broadcast_board_event',
                            lambda board_id, payload: sent.append((str(board_id), payload)))
        with TestCase.captureOnCommitCallbacks() as callbacks:
            place = add_place_to_board(board, 'Colosseo', 41.8902, 12.4922)
        assert sent == [], 'prima del commit non si invia niente'
        for callback in callbacks:
            callback()
        assert sent == [(str(board.id), place_event('Colosseo', str(place.id)))]


@pytest.mark.django_db(transaction=True)
class TestBoardConsumer:
    """Passo 3: connessione con le policy, eventi, sola ricezione."""

    def test_owner_receives_place_fragment(self, board, people, inmemory_channel_layer):
        async def scenario():
            comm = communicator(board.id, people[0])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            assert connected
            await sync_to_async(realtime.broadcast_board_event)(board.id, place_event('Pantheon', 'p7'))
            html = await comm.receive_from(timeout=TIMEOUT)
            await comm.disconnect()
            return html

        html = async_to_sync(scenario)()
        assert 'hx-swap-oob="beforeend:#place-list"' in html
        assert '<li id="place-p7">Pantheon</li>' in html

    def test_collaborator_receives(self, board, people, inmemory_channel_layer):
        async def scenario():
            comm = communicator(board.id, people[1])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            assert connected
            await sync_to_async(realtime.broadcast_board_event)(board.id, place_event())
            html = await comm.receive_from(timeout=TIMEOUT)
            await comm.disconnect()
            return html

        assert 'Colosseo' in async_to_sync(scenario)()

    @pytest.mark.parametrize('who', ['stranger', 'anonymous', 'unknown_board'])
    def test_rejected(self, who, board, people, inmemory_channel_layer):
        from django.contrib.auth.models import AnonymousUser
        import uuid
        owner, _, stranger = people
        target = {'stranger': (board.id, stranger), 'anonymous': (board.id, AnonymousUser()),
                  'unknown_board': (uuid.uuid4(), owner)}[who]

        async def scenario():
            ok = communicator(board.id, owner)
            owner_connected, _ = await ok.connect(timeout=TIMEOUT)
            await ok.disconnect()
            comm = communicator(*target)
            connected, code = await comm.connect(timeout=TIMEOUT)
            return owner_connected, connected, code

        owner_connected, connected, code = async_to_sync(scenario)()
        assert owner_connected, 'il proprietario si connette'
        assert not connected
        assert code == 4403

    def test_permission_rechecked_on_each_event(self, board, people, inmemory_channel_layer):
        viewer = people[1]

        async def scenario():
            comm = communicator(board.id, viewer)
            connected, _ = await comm.connect(timeout=TIMEOUT)
            assert connected
            await database_sync_to_async(Collaborator.objects.filter(user=viewer).delete)()
            await sync_to_async(realtime.broadcast_board_event)(board.id, place_event())
            return await comm.receive_output(timeout=TIMEOUT)

        message = async_to_sync(scenario)()
        assert message['type'] == 'websocket.close'
        assert message.get('code') == 4403

    def test_browser_messages_are_ignored(self, board, people, inmemory_channel_layer):
        async def scenario():
            comm = communicator(board.id, people[0])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            await comm.send_to(text_data='{"name": "dal browser"}')
            nothing = await comm.receive_nothing(timeout=0.5)
            await comm.disconnect()
            return connected, nothing

        assert async_to_sync(scenario)() == (True, True)

    def test_disconnect_leaves_group(self, board, people, inmemory_channel_layer):
        layer = inmemory_channel_layer

        async def scenario():
            comm = communicator(board.id, people[0])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            members = len(layer.groups.get(f'board_{board.id}', {}))
            await comm.disconnect()
            return connected, members, len(layer.groups.get(f'board_{board.id}', {}))

        assert async_to_sync(scenario)() == (True, 1, 0)

    def test_service_to_browser(self, board, people, inmemory_channel_layer):
        async def scenario():
            comm = communicator(board.id, people[1])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            assert connected
            # transaction=True: niente transazione del test, on_commit parte subito dopo il salvataggio
            await database_sync_to_async(add_place_to_board)(board, 'Fontana di Trevi', 41.9009, 12.4833)
            html = await comm.receive_from(timeout=TIMEOUT)
            await comm.disconnect()
            return html

        assert 'Fontana di Trevi' in async_to_sync(scenario)()


@pytest.mark.django_db(transaction=True)
class TestAsgiApplication:
    """Passo 5: routing ASGI, sessione e controllo dell'origine."""

    def _cookie(self, user):
        client = Client()
        client.force_login(user)
        return f'{settings.SESSION_COOKIE_NAME}={client.cookies[settings.SESSION_COOKIE_NAME].value}'

    def _connect(self, board, cookie, origin):
        from palestra.asgi import application

        async def scenario():
            comm = WebsocketCommunicator(application, f'/ws/boards/{board.id}/',
                                         headers=[(b'cookie', cookie.encode()), (b'origin', origin)])
            connected, _ = await comm.connect(timeout=TIMEOUT)
            await comm.disconnect()
            return connected

        return async_to_sync(scenario)()

    def test_session_user_connects(self, board, people, inmemory_channel_layer):
        cookie = self._cookie(people[0])
        assert self._connect(board, cookie, b'http://localhost') is True
        stranger_cookie = self._cookie(people[2])
        assert self._connect(board, stranger_cookie, b'http://localhost') is False

    def test_foreign_origin_rejected(self, board, people, inmemory_channel_layer):
        cookie = self._cookie(people[0])
        assert self._connect(board, cookie, b'http://localhost') is True
        assert self._connect(board, cookie, b'https://evil.example') is False


@pytest.mark.django_db
class TestBoardPage:
    """Passo 4: la pagina della bacheca si collega al WebSocket."""

    def test_fragment(self):
        html = render_to_string('boards/_place_oob.html', {'place': {'id': 'p1', 'name': '<b>Bar</b>'}})
        assert 'hx-swap-oob="beforeend:#place-list"' in html
        assert '<li id="place-p1">&lt;b&gt;Bar&lt;/b&gt;</li>' in html
        assert 'id="place-empty" hx-swap-oob="delete"' in html

    def test_detail_connects_websocket(self, board, people):
        client = Client()
        client.force_login(people[1])
        html = client.get(f'/boards/{board.id}/').content.decode()
        assert 'hx-ext="ws"' in html
        assert f'ws-connect="/ws/boards/{board.id}/"' in html
        assert '/static/core/ext/ws.js' in html
        assert html.index('hx-ext="ws"') < html.index('id="place-list"'), 'la lista sta dentro il blocco ws'
        assert 'id="place-empty"' in html
        path = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'ext', 'ws.js')
        with open(path, encoding='utf-8') as f:
            assert "defineExtension('ws'" in f.read(), 'estensione ws vendorizzata'

    def test_ws_extension_only_on_board_page(self, board, people):
        client = Client()
        client.force_login(people[0])
        html = client.get('/boards/').content.decode()
        assert '/static/core/ext/ws.js' in client.get(f'/boards/{board.id}/').content.decode()
        assert 'ws.js' not in html and 'ws-connect' not in html
