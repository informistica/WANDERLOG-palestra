"""Modelli base comuni a tutte le app."""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Modello astratto base per tutti i modelli del progetto.
    Fornisce un ID UUID e timestamp di creazione/modifica.
    """
    # TODO: Aggiungi campo id come UUIDField con primary_key=True
    # id = models.UUIDField(...)
    
    # TODO: Aggiungi created_at con auto_now_add=True
    # created_at = models.DateTimeField(...)
    
    # TODO: Aggiungi updated_at con auto_now=True  
    # updated_at = models.DateTimeField(...)

    class Meta:
        abstract = True
