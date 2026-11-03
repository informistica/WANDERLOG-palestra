
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("boards", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Collaborator",
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
                    "role",
                    models.CharField(
                        choices=[("viewer", "Lettore")],
                        default="viewer",
                        max_length=20,
                        verbose_name="Ruolo",
                    ),
                ),
                (
                    "board",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborators",
                        to="boards.board",
                        verbose_name="Bacheca",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Utente",
                    ),
                ),
            ],
            options={
                "verbose_name": "Collaboratore",
                "verbose_name_plural": "Collaboratori",
                "unique_together": {("board", "user")},
            },
        ),
    ]
