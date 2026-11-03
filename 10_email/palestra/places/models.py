"""Modelli per luoghi."""
from django.db import models
from core.models import BaseModel


class Place(BaseModel):
    """Luogo preferito in una bacheca."""
    name = models.CharField(max_length=255, verbose_name='Nome')
    lat = models.FloatField(verbose_name='Latitudine')
    lng = models.FloatField(verbose_name='Longitudine')
    description = models.TextField(blank=True, verbose_name='Descrizione')
    # compilato dal task geocode_place (livello 08)
    address = models.CharField(max_length=255, blank=True, verbose_name='Indirizzo')
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='places',
        verbose_name='Bacheca'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Luogo'
        verbose_name_plural = 'Luoghi'
        ordering = ['created_at']
