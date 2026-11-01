"""Modelli per luoghi."""
from django.db import models
from core.models import BaseModel


class Place(BaseModel):
    """Luogo preferito in una bacheca."""
    # TODO: Aggiungi campo name
    # name = models.CharField(...)
    
    # TODO: Aggiungi coordinate geografiche lat e lng
    # lat = models.FloatField(...)
    # lng = models.FloatField(...)
    
    # TODO: Aggiungi campo description (opzionale)
    # description = models.TextField(...)
    
    # TODO: Aggiungi FK board verso 'boards.Board' con related_name='places'
    # board = models.ForeignKey(...)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Luogo'
        verbose_name_plural = 'Luoghi'
        ordering = ['created_at']
