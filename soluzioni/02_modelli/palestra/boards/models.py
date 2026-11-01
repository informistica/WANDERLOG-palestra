"""Modelli per bacheche e utenti."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from core.models import BaseModel


class UserManager(BaseUserManager):
    """Manager personalizzato per User senza username."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crea e salva un utente normale."""
        if not email:
            raise ValueError('Email è obbligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crea e salva un superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Utente personalizzato che usa email al posto di username.
    Ha UUID come chiave primaria.
    """
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='Email')
    name = models.CharField(max_length=255, blank=True, verbose_name='Nome')
    language = models.CharField(
        max_length=2,
        choices=[('it', 'Italiano'), ('en', 'English')],
        default='it',
        verbose_name='Lingua'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    def __str__(self):
        return self.email


class Board(BaseModel):
    """Bacheca di luoghi preferiti."""
    title = models.CharField(max_length=255, verbose_name='Titolo')
    description = models.TextField(blank=True, verbose_name='Descrizione')
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='boards',
        verbose_name='Proprietario'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Bacheca'
        verbose_name_plural = 'Bacheche'
