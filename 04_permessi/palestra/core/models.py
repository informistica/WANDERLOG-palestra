"""Modelli base comuni a tutte le app."""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Modello astratto base per tutti i modelli del progetto.
    Fornisce un ID UUID e timestamp di creazione/modifica.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
