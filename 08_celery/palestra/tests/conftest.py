"""Fixture comuni: nei test i task Celery girano subito, nello stesso processo (niente worker)."""
import pytest


@pytest.fixture(autouse=True)
def celery_eager():
    from palestra.celery import app
    app.conf.task_always_eager = True
    app.conf.task_eager_propagates = True
    yield
