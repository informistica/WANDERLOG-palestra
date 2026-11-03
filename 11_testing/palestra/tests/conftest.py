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
# TODO (passo 3): implementa le fixture usando le factory. Tutte function-scoped.
#   owner, stranger: due utenti (owner@example.com, stranger@example.com)
#   board: bacheca 'Roma' di owner
#   collaborator: l'UTENTE (non il Collaborator) con accesso in lettura a board
#   place: 'Colosseo' (41.8902, 12.4922) in board
#   owner_client: il fixture `client` di pytest-django con force_login(owner)
#   api_client_owner: rest_framework.test.APIClient con force_authenticate(owner)


def _da_fare(nome):
    raise NotImplementedError(f'TODO passo 3: fixture {nome}')


@pytest.fixture
def owner(db):
    _da_fare('owner')


@pytest.fixture
def stranger(db):
    _da_fare('stranger')


@pytest.fixture
def board(owner):
    _da_fare('board')


@pytest.fixture
def collaborator(board):
    _da_fare('collaborator')


@pytest.fixture
def place(board):
    _da_fare('place')


@pytest.fixture
def owner_client(client, owner):
    _da_fare('owner_client')


@pytest.fixture
def api_client_owner(owner):
    _da_fare('api_client_owner')