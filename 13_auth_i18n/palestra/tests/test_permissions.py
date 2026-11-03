"""Test per il sistema di permessi."""
import pytest
from django.contrib.auth import get_user_model
from boards.models import Board, Collaborator
from boards.services import add_collaborator
from boards.policies import can_view_board, can_edit_board, can_add_collaborator


User = get_user_model()


@pytest.mark.django_db
class TestCollaboratorModel:
    """Test per il modello Collaborator."""
    
    def test_create_collaborator(self):
        """Deve essere possibile creare un Collaborator."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        collaborator = Collaborator.objects.create(
            board=board,
            user=viewer,
            role='viewer'
        )
        
        assert collaborator.board == board
        assert collaborator.user == viewer
        assert collaborator.role == 'viewer'
    
    def test_collaborator_unique_constraint(self):
        """Non si può aggiungere lo stesso user due volte alla stessa board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        Collaborator.objects.create(board=board, user=viewer)
        
        with pytest.raises(Exception):  # IntegrityError
            Collaborator.objects.create(board=board, user=viewer)


@pytest.mark.django_db
class TestBoardPolicies:
    """Test per le policy delle board."""
    
    def test_owner_can_view(self):
        """Il proprietario può visualizzare la board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        assert can_view_board(owner, board) is True
    
    def test_collaborator_can_view(self):
        """Un collaborator può visualizzare la board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        Collaborator.objects.create(board=board, user=viewer)
        
        assert can_view_board(viewer, board) is True
    
    def test_stranger_cannot_view(self):
        """Un utente esterno non può visualizzare la board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        stranger = User.objects.create_user(email='stranger@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        assert can_view_board(stranger, board) is False
    
    def test_owner_can_edit(self):
        """Il proprietario può modificare la board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        assert can_edit_board(owner, board) is True
    
    def test_collaborator_cannot_edit(self):
        """Un collaborator non può modificare la board."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        Collaborator.objects.create(board=board, user=viewer)
        
        assert can_edit_board(viewer, board) is False
    
    def test_owner_can_add_collaborator(self):
        """Il proprietario può aggiungere collaboratori."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        assert can_add_collaborator(owner, board) is True
    
    def test_collaborator_cannot_add_collaborator(self):
        """Un collaborator non può aggiungere altri collaboratori."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        Collaborator.objects.create(board=board, user=viewer)
        
        assert can_add_collaborator(viewer, board) is False


@pytest.mark.django_db
class TestCollaboratorService:
    """Test per il service add_collaborator."""
    
    def test_add_collaborator_success(self):
        """add_collaborator deve aggiungere un collaborator."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        collaborator = add_collaborator(board, viewer, requesting_user=owner)
        
        assert collaborator.board == board
        assert collaborator.user == viewer
        assert collaborator.role == 'viewer'
        assert Collaborator.objects.count() == 1
    
    def test_add_collaborator_without_permission_fails(self):
        """Non si può aggiungere un collaborator senza permessi."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        viewer = User.objects.create_user(email='viewer@example.com', password='test123')
        other = User.objects.create_user(email='other@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        with pytest.raises(PermissionError):
            add_collaborator(board, other, requesting_user=viewer)
    
    def test_cannot_add_owner_as_collaborator(self):
        """Il proprietario non può essere aggiunto come collaborator."""
        owner = User.objects.create_user(email='owner@example.com', password='test123')
        board = Board.objects.create(title='Test', owner=owner)
        
        with pytest.raises(ValueError, match='proprietario'):
            add_collaborator(board, owner, requesting_user=owner)
