"""Test per templates e HTMX."""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from boards.models import Board, Collaborator

User = get_user_model()


@pytest.mark.django_db
class TestTemplates:
    """Test per template rendering."""
    
    def test_base_template_has_htmx(self):
        """Il template base deve includere HTMX CDN."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        client = Client()
        client.force_login(user)
        
        response = client.get('/boards/')
        
        assert response.status_code == 200
        assert b'htmx' in response.content.lower()
    
    def test_board_list_full_page(self):
        """GET /boards/ senza HX-Request deve renderizzare pagina completa."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        Board.objects.create(title='Test Board', owner=user)
        
        client = Client()
        client.force_login(user)
        response = client.get('/boards/')
        
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.content or b'<html' in response.content
        assert b'Test Board' in response.content
    
    def test_board_list_partial_with_hx_request(self):
        """GET /boards/ con HX-Request deve renderizzare solo il partial."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        Board.objects.create(title='Test Board', owner=user)
        
        client = Client()
        client.force_login(user)
        response = client.get('/boards/', HTTP_HX_REQUEST='true')
        
        assert response.status_code == 200
        # Partial non deve avere DOCTYPE o html completo
        assert b'<!DOCTYPE' not in response.content
        assert b'Test Board' in response.content
    
    def test_csrf_token_in_response(self):
        """Le pagine devono includere CSRF token per HTMX."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = Client()
        client.force_login(user)
        response = client.get('/boards/')
        
        assert response.status_code == 200
        assert b'csrf' in response.content.lower()
    
    def test_board_create_form_validation_errors_as_partial(self):
        """POST con errori deve re-renderizzare form con errori come partial."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = Client()
        client.force_login(user)
        # Post con title mancante
        response = client.post('/boards/create/', {}, HTTP_HX_REQUEST='true')
        
        # Deve tornare partial con errori (non redirect)
        assert response.status_code == 200
        assert b'error' in response.content.lower() or b'required' in response.content.lower()
    
    def test_board_permissions_viewer_cannot_delete(self):
        """Un collaborator viewer non deve poter cancellare una board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Shared Board', owner=owner)
        Collaborator.objects.create(board=board, user=viewer, role='viewer')
        
        client = Client()
        client.force_login(viewer)
        response = client.post(f'/boards/{board.id}/delete/')
        
        # Deve essere rifiutato (403 o redirect)
        assert response.status_code in [403, 302, 404]
    
    def test_aria_live_region_present(self):
        """Deve esserci un region aria-live per updates dinamici."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = Client()
        client.force_login(user)
        response = client.get('/boards/')
        
        assert response.status_code == 200
        assert b'aria-live' in response.content


@pytest.mark.django_db
class TestI18n:
    """Test per internazionalizzazione."""
    
    def test_italian_translation_present(self):
        """Le pagine devono contenere traduzioni in italiano."""
        user = User.objects.create_user(email='test@example.com', password='test123')
        
        client = Client()
        client.force_login(user)
        response = client.get('/boards/', HTTP_ACCEPT_LANGUAGE='it')
        
        assert response.status_code == 200
        # Verifica presenza di parole italiane comuni
        content_lower = response.content.lower()
        # Almeno una parola italiana dovrebbe essere presente
        assert any(word in content_lower for word in [b'bachec', b'titolo', b'descrizione', b'crea'])
