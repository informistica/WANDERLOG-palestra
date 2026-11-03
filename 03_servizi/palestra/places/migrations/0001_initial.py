
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("boards", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Place",
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
                ("name", models.CharField(max_length=255, verbose_name="Nome")),
                ("lat", models.FloatField(verbose_name="Latitudine")),
                ("lng", models.FloatField(verbose_name="Longitudine")),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Descrizione"),
                ),
                (
                    "board",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="places",
                        to="boards.board",
                        verbose_name="Bacheca",
                    ),
                ),
            ],
            options={
                "verbose_name": "Luogo",
                "verbose_name_plural": "Luoghi",
                "ordering": ["created_at"],
            },
        ),
    ]
