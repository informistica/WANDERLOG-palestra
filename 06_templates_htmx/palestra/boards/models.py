"""Modelli per bacheche e utenti."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from core.models import BaseModel


class UserManager(BaseUserManager):
    """Manager personalizzato per User senza username."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email è obbligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
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


class Collaborator(BaseModel):
    """TODO: Collaboratore di una board."""
    # TODO: Aggiungi board FK a Board, related_name='collaborators'
    # TODO: Aggiungi user FK a User, related_name='collaborations'
    # TODO: Aggiungi role CharField con choices [('viewer', 'Visualizzatore')], default='viewer'
    pass
    
    # TODO: Aggiungi __str__ che ritorna f"{self.user.email} - {self.board.title}"
    
    class Meta:
        # TODO: Aggiungi unique_together = ('board', 'user')
        verbose_name = 'Collaboratore'
        verbose_name_plural = 'Collaboratori'
