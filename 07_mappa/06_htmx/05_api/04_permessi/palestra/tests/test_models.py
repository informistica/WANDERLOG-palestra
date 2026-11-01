"""Test per verificare i modelli Django."""
import pytest
from django.db import models
from django.contrib.auth import get_user_model
from boards.models import Board
from places.models import Place
from core.models import BaseModel


User = get_user_model()


@pytest.mark.django_db
class TestBaseModel:
    """Test per il modello base."""
    
    def test_basemodel_has_uuid_pk(self):
        """BaseModel deve avere UUID come primary key."""
        assert hasattr(BaseModel, '_meta')
        id_field = BaseModel._meta.get_field('id')
        assert isinstance(id_field, models.UUIDField)
        assert id_field.primary_key
        
    def test_basemodel_has_timestamps(self):
        """BaseModel deve avere created_at e updated_at."""
        assert hasattr(BaseModel, '_meta')
        created_field = BaseModel._meta.get_field('created_at')
        updated_field = BaseModel._meta.get_field('updated_at')
        assert isinstance(created_field, models.DateTimeField)
        assert isinstance(updated_field, models.DateTimeField)
        assert created_field.auto_now_add
        assert updated_field.auto_now


@pytest.mark.django_db
class TestUser:
    """Test per il modello User."""
    
    def test_user_model_is_configured(self):
        """User deve essere il modello auth configurato."""
        from django.conf import settings
        assert settings.AUTH_USER_MODEL == 'boards.User'
    
    def test_user_has_uuid_pk(self):
        """User deve avere UUID come primary key."""
        id_field = User._meta.get_field('id')
        assert isinstance(id_field, models.UUIDField)
        assert id_field.primary_key
    
    def test_user_username_field_is_email(self):
        """User deve usare email come USERNAME_FIELD."""
        assert User.USERNAME_FIELD == 'email'
    
    def test_user_no_username_field(self):
        """User non deve avere il campo username."""
        try:
            User._meta.get_field('username')
            pytest.fail("User non dovrebbe avere il campo username")
        except models.FieldDoesNotExist:
            pass  # Corretto!
    
    def test_create_user(self):
        """Deve essere possibile creare un utente con email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        assert user.email == 'test@example.com'
        assert user.name == 'Test User'
        assert user.check_password('testpass123')
        assert user.language == 'it'  # default
    
    def test_user_str(self):
        """__str__ deve ritornare l'email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'test@example.com'


@pytest.mark.django_db
class TestBoard:
    """Test per il modello Board."""
    
    def test_board_inherits_basemodel(self):
        """Board deve ereditare da BaseModel."""
        assert issubclass(Board, BaseModel)
    
    def test_create_board(self):
        """Deve essere possibile creare una Board."""
        user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        board = Board.objects.create(
            title='Luoghi Preferiti',
            description='La mia bacheca',
            owner=user
        )
        assert board.title == 'Luoghi Preferiti'
        assert board.owner == user
        assert hasattr(board, 'id')
        assert hasattr(board, 'created_at')
        assert hasattr(board, 'updated_at')
    
    def test_board_str(self):
        """__str__ deve ritornare il title."""
        user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        board = Board.objects.create(
            title='Luoghi Preferiti',
            owner=user
        )
        assert str(board) == 'Luoghi Preferiti'


@pytest.mark.django_db
class TestPlace:
    """Test per il modello Place."""
    
    def test_place_inherits_basemodel(self):
        """Place deve ereditare da BaseModel."""
        assert issubclass(Place, BaseModel)
    
    def test_create_place(self):
        """Deve essere possibile creare un Place."""
        user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        board = Board.objects.create(
            title='Luoghi Preferiti',
            owner=user
        )
        place = Place.objects.create(
            name='Colosseo',
            lat=41.8902,
            lng=12.4922,
            description='Anfiteatro Flavio',
            board=board
        )
        assert place.name == 'Colosseo'
        assert place.lat == 41.8902
        assert place.lng == 12.4922
        assert place.board == board
        assert hasattr(place, 'id')
        assert hasattr(place, 'created_at')
    
    def test_place_str(self):
        """__str__ deve ritornare il name."""
        user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        board = Board.objects.create(
            title='Luoghi Preferiti',
            owner=user
        )
        place = Place.objects.create(
            name='Colosseo',
            lat=41.8902,
            lng=12.4922,
            board=board
        )
        assert str(place) == 'Colosseo'
    
    def test_place_related_name(self):
        """Board deve avere related_name='places'."""
        user = User.objects.create_user(
            email='owner@example.com',
            password='testpass123'
        )
        board = Board.objects.create(
            title='Luoghi Preferiti',
            owner=user
        )
        place = Place.objects.create(
            name='Colosseo',
            lat=41.8902,
            lng=12.4922,
            board=board
        )
        assert board.places.count() == 1
        assert board.places.first() == place
