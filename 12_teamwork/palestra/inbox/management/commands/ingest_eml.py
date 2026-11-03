"""python manage.py ingest_eml file.eml [altro.eml ...]"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from inbox.services import ingest_eml


class Command(BaseCommand):
    help = "Elabora uno o piu' file .eml come se fossero arrivati all'indirizzo della bacheca"

    def add_arguments(self, parser):
        parser.add_argument('paths', nargs='+', help='file .eml da importare')

    def handle(self, *args, **options):
        for path in options['paths']:
            try:
                raw = Path(path).read_bytes()
            except OSError as exc:
                raise CommandError(f'Non riesco a leggere {path}: {exc}') from exc
            record = ingest_eml(raw)
            line = f'{path}: {record.status}'
            if record.reason:
                line += f' ({record.reason})'
            if record.place:
                line += f' -> {record.place.name}'
            self.stdout.write(line)
