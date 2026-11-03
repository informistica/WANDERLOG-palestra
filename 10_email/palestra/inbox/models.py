"""Modelli dell'app inbox: indirizzi delle bacheche ed email ricevute."""
import secrets

from django.db import models

from core.models import BaseModel


def new_token():
    """16 caratteri esadecimali: difficili da indovinare, facili da copiare."""
    return secrets.token_hex(8)


class InboundAddress(BaseModel):
    """L'indirizzo board+<token>@dominio di una bacheca."""
    board = models.OneToOneField(
        'boards.Board',
        on_delete=models.CASCADE,
        related_name='inbound_address',
        verbose_name='Bacheca'
    )
    token = models.CharField(max_length=32, unique=True, default=new_token, verbose_name='Token')

    def __str__(self):
        return f'board+{self.token}'

    class Meta:
        verbose_name = 'Indirizzo email della bacheca'
        verbose_name_plural = 'Indirizzi email delle bacheche'


class InboundEmail(BaseModel):
    """Ogni email ricevuta, con l'esito: anche quelle scartate restano tracciate."""
    STATUS_PARSED = 'parsed'
    STATUS_UNRECOGNIZED = 'unrecognized'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PARSED, 'Luogo aggiunto'),
        (STATUS_UNRECOGNIZED, 'Nessun luogo riconosciuto'),
        (STATUS_REJECTED, 'Scartata'),
    ]

    sender = models.CharField(max_length=255, blank=True, verbose_name='Mittente')
    recipient = models.CharField(max_length=255, blank=True, verbose_name='Destinatari')
    subject = models.CharField(max_length=255, blank=True, verbose_name='Oggetto')
    message_id = models.CharField(max_length=255, blank=True, db_index=True, verbose_name='Message-ID')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Esito')
    reason = models.CharField(max_length=255, blank=True, verbose_name='Motivo')
    board = models.ForeignKey(
        'boards.Board',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbound_emails',
        verbose_name='Bacheca'
    )
    place = models.ForeignKey(
        'places.Place',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inbound_emails',
        verbose_name='Luogo creato'
    )

    def __str__(self):
        return f'{self.sender}: {self.subject} ({self.status})'

    class Meta:
        verbose_name = 'Email ricevuta'
        verbose_name_plural = 'Email ricevute'
        ordering = ['-created_at']
