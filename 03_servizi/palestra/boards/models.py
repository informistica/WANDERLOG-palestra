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
    # TODO: Rimuovi il campo username
    # username = None
    
    # TODO: Aggiungi id come UUIDField primary key
    # id = models.UUIDField(...)
    
    # TODO: Rendi email unica e obbligatoria
    # email = models.EmailField(unique=True, ...)
    
    # TODO: Aggiungi campo name per il nome completo
    # name = models.CharField(...)
    
    # TODO: Aggiungi campo language con scelte 'it', 'en' e default 'it'
    # language = models.CharField(max_length=2, choices=[('it', 'Italiano'), ('en', 'English')], default='it')
    
    # TODO: Imposta USERNAME_FIELD e REQUIRED_FIELDS
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []
    
    # TODO: Usa il manager personalizzato
    # objects = UserManager()

    def __str__(self):
        return self.email


class Board(BaseModel):
    """Bacheca di luoghi preferiti."""
    # TODO: Aggiungi campo title
    # title = models.CharField(...)
    
    # TODO: Aggiungi campo description (opzionale, blank=True)
    # description = models.TextField(...)
    
    # TODO: Aggiungi FK owner verso User con related_name='boards'
    # owner = models.ForeignKey(...)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Bacheca'
        verbose_name_plural = 'Bacheche'
