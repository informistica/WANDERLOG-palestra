"""python manage.py ingest_eml file.eml [altro.eml ...]"""
from pathlib import Path  # noqa: F401

from django.core.management.base import BaseCommand, CommandError  # noqa: F401

from inbox.services import ingest_eml  # noqa: F401


class Command(BaseCommand):
    help = "Elabora uno o piu' file .eml come se fossero arrivati all'indirizzo della bacheca"

    def add_arguments(self, parser):
        parser.add_argument('paths', nargs='+', help='file .eml da importare')

    def handle(self, *args, **options):
        # TODO (passo 6): per ogni percorso leggi i bytes (OSError -> CommandError),
        #   chiama ingest_eml e scrivi su self.stdout una riga '<file>: <status> ...'
        raise NotImplementedError('TODO passo 6: comando ingest_eml')
