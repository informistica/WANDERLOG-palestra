"""Test dell'admin (passo 5)."""
import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model

from boards.models import Board
from places.models import Place

User = get_user_model()


def test_models_registered_in_admin():
    for model in (User, Board, Place):
        assert model in admin.site._registry, f"{model.__name__} non è registrato nell'admin"


@pytest.mark.django_db
def test_admin_user_pages_work_without_username(client):
    superuser = User.objects.create_superuser(email='admin@example.com', password='pass12345')
    client.force_login(superuser)
    assert client.get('/admin/boards/user/').status_code == 200
    assert client.get('/admin/boards/user/add/').status_code == 200
    assert client.get(f'/admin/boards/user/{superuser.pk}/change/').status_code == 200
