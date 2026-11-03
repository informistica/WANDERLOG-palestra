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
