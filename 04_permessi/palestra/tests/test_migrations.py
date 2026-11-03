"""Le migrazioni esistono e sono allineate ai modelli (passo 6)."""
import os
from io import StringIO

import pytest
from django.core.management import call_command

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.parametrize('app', ['boards', 'places'])
def test_initial_migration_exists(app):
    assert os.path.exists(os.path.join(PROJECT, app, 'migrations', '0001_initial.py')), (
        f"Manca {app}/migrations/0001_initial.py: esegui makemigrations"
    )


@pytest.mark.django_db
def test_no_missing_migrations():
    from django.apps import apps
    for app in ('core', 'boards', 'places'):
        assert apps.is_installed(app), f"L'app {app} non è in INSTALLED_APPS"
    out = StringIO()
    try:
        call_command('makemigrations', '--check', '--dry-run', stdout=out, stderr=out)
    except SystemExit:
        pytest.fail("Ci sono modifiche ai modelli senza migrazione:\n" + out.getvalue())
