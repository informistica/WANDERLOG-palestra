
import django.db.models.deletion
import inbox.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("boards", "0002_collaborator"),
        ("places", "0002_place_address"),
    ]

    operations = [
        migrations.CreateModel(
            name="InboundAddress",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "token",
                    models.CharField(
                        default=inbox.models.new_token,
                        max_length=32,
                        unique=True,
                        verbose_name="Token",
                    ),
                ),
                (
                    "board",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inbound_address",
                        to="boards.board",
                        verbose_name="Bacheca",
                    ),
                ),
            ],
            options={
                "verbose_name": "Indirizzo email della bacheca",
                "verbose_name_plural": "Indirizzi email delle bacheche",
            },
        ),
        migrations.CreateModel(
            name="InboundEmail",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "sender",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Mittente"
                    ),
                ),
                (
                    "recipient",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Destinatari"
                    ),
                ),
                (
                    "subject",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Oggetto"
                    ),
                ),
                (
                    "message_id",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=255,
                        verbose_name="Message-ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("parsed", "Luogo aggiunto"),
                            ("unrecognized", "Nessun luogo riconosciuto"),
                            ("rejected", "Scartata"),
                        ],
                        max_length=20,
                        verbose_name="Esito",
                    ),
                ),
                (
                    "reason",
                    models.CharField(blank=True, max_length=255, verbose_name="Motivo"),
                ),
                (
                    "board",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inbound_emails",
                        to="boards.board",
                        verbose_name="Bacheca",
                    ),
                ),
                (
                    "place",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inbound_emails",
                        to="places.place",
                        verbose_name="Luogo creato",
                    ),
                ),
            ],
            options={
                "verbose_name": "Email ricevuta",
                "verbose_name_plural": "Email ricevute",
                "ordering": ["-created_at"],
            },
        ),
    ]
