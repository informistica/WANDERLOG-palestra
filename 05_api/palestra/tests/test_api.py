"""Test per API REST."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from boards.models import Board
from places.models import Place

User = get_user_model()


@pytest.mark.django_db
class TestBoardAPI:
    """Test per API boards."""
    
    def test_list_boards(self):
        """GET /api/v1/boards/ deve listare boards dell'utente."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        Board.objects.create(title='My Board', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/boards/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
    
    def test_create_board(self):
        """POST /api/v1/boards/ deve creare una board."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/v1/boards/', {
            'title': 'New Board',
            'description': 'Test'
        })
        
        assert response.status_code == 201
        assert Board.objects.count() == 1
        assert Board.objects.first().owner == user


@pytest.mark.django_db
class TestPlaceAPI:
    """Test per API places."""
    
    def test_list_places(self):
        """GET /api/v1/places/ deve listare places."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=user)
        Place.objects.create(name='Colosseo', lat=41.89, lng=12.49, board=board)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/places/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
