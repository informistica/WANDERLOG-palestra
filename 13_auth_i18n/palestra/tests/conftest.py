"""Fixture comuni del progetto."""
import pytest


@pytest.fixture(autouse=True)
def celery_eager():
    """Nei test i task Celery girano subito, nello stesso processo (niente worker)."""
    from palestra.celery import app
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True
    yield


@pytest.fixture
def inmemory_channel_layer(settings):
    """Channel layer in memoria: veloce e isolato. Channels lo ricrea a ogni cambio di settings."""
    settings.CHANNEL_LAYERS = {'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
    from channels.layers import get_channel_layer
    return get_channel_layer()


# --- livello 11: fixture costruite sulle factory (tests/factories.py) ---
# I file di test che definiscono una fixture con lo stesso nome usano la propria.

@pytest.fixture
def owner(db):
    from tests.factories import UserFactory
    return UserFactory(email='owner@example.com')


@pytest.fixture
def stranger(db):
    from tests.factories import UserFactory
    return UserFactory(email='stranger@example.com')


@pytest.fixture
def board(owner):
    from tests.factories import BoardFactory
    return BoardFactory(owner=owner, title='Roma')


@pytest.fixture
def collaborator(board):
    """Un utente con accesso in lettura a `board`."""
    from tests.factories import CollaboratorFactory
    return CollaboratorFactory(board=board, user__email='collaborator@example.com').user


@pytest.fixture
def place(board):
    from tests.factories import PlaceFactory
    return PlaceFactory(board=board, name='Colosseo', lat=41.8902, lng=12.4922)


@pytest.fixture
def owner_client(client, owner):
    """Client Django con la sessione del proprietario."""
    client.force_login(owner)
    return client


@pytest.fixture
def api_client_owner(owner):
    """APIClient di DRF autenticato come proprietario."""
    from rest_framework.test import APIClient
    api = APIClient()
    api.force_authenticate(user=owner)
    return api