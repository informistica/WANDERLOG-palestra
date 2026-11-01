"""Test per API REST."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from boards.models import Board, Collaborator
from places.models import Place

User = get_user_model()


@pytest.mark.django_db
class TestBoardAPI:
    """Test per API boards."""
    
    def test_list_boards_authenticated(self):
        """GET /api/v1/boards/ deve listare boards dell'utente."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        Board.objects.create(title='My Board', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/boards/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
    
    def test_list_boards_unauthenticated(self):
        """GET /api/v1/boards/ senza autenticazione deve essere rifiutato."""
        client = APIClient()
        response = client.get('/api/v1/boards/')
        
        assert response.status_code in [401, 403]
    
    def test_create_board(self):
        """POST /api/v1/boards/ deve creare una board con owner=request.user."""
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
    
    def test_detail_board_owner(self):
        """GET /api/v1/boards/{id}/ deve mostrare dettaglio al proprietario."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='My Board', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f'/api/v1/boards/{board.id}/')
        
        assert response.status_code == 200
        assert response.data['title'] == 'My Board'
    
    def test_detail_board_collaborator(self):
        """GET /api/v1/boards/{id}/ deve mostrare dettaglio a un collaboratore."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        collaborator = User.objects.create_user(email='collab@example.com', password='test123')
        board = Board.objects.create(title='Shared Board', owner=owner)
        Collaborator.objects.create(board=board, user=collaborator, role='viewer')
        
        client = APIClient()
        client.force_authenticate(user=collaborator)
        response = client.get(f'/api/v1/boards/{board.id}/')
        
        assert response.status_code == 200
        assert response.data['title'] == 'Shared Board'
    
    def test_detail_board_non_collaborator(self):
        """GET /api/v1/boards/{id}/ deve rifiutare un non-collaborator con 404."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        other = User.objects.create_user(email='other@example.com', password='test123')
        board = Board.objects.create(title='Private Board', owner=owner)
        
        client = APIClient()
        client.force_authenticate(user=other)
        response = client.get(f'/api/v1/boards/{board.id}/')
        
        assert response.status_code == 404
    
    def test_update_board_owner(self):
        """PUT /api/v1/boards/{id}/ deve permettere aggiornamento al proprietario."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='Old Title', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.put(f'/api/v1/boards/{board.id}/', {
            'title': 'New Title',
            'description': 'Updated'
        })
        
        assert response.status_code == 200
        board.refresh_from_db()
        assert board.title == 'New Title'
    
    def test_delete_board_owner(self):
        """DELETE /api/v1/boards/{id}/ deve permettere cancellazione al proprietario."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='To Delete', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.delete(f'/api/v1/boards/{board.id}/')
        
        assert response.status_code == 204
        assert Board.objects.count() == 0


@pytest.mark.django_db
class TestPlaceAPI:
    """Test per API places."""
    
    def test_list_places_authenticated(self):
        """GET /api/v1/places/ deve listare places delle board accessibili."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=user)
        Place.objects.create(name='Colosseo', lat=41.89, lng=12.49, board=board)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/places/')
        
        assert response.status_code == 200
        assert len(response.data['results']) == 1
    
    def test_list_places_unauthenticated(self):
        """GET /api/v1/places/ senza autenticazione deve essere rifiutato."""
        client = APIClient()
        response = client.get('/api/v1/places/')
        
        assert response.status_code in [401, 403]
    
    def test_create_place(self):
        """POST /api/v1/places/ deve creare un place."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=user)
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post('/api/v1/places/', {
            'name': 'Torre Eiffel',
            'lat': 48.8584,
            'lng': 2.2945,
            'description': 'Paris',
            'board': str(board.id)
        })
        
        assert response.status_code == 201
        assert Place.objects.count() == 1
        assert Place.objects.first().name == 'Torre Eiffel'
    
    def test_api_prefix(self):
        """Verifica che l'API sia accessibile al prefix /api/v1/."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = APIClient()
        client.force_authenticate(user=user)
        
        # Verifica boards
        response = client.get('/api/v1/boards/')
        assert response.status_code == 200
        
        # Verifica places
        response = client.get('/api/v1/places/')
        assert response.status_code == 200
