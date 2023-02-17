from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    commands = [
        ("import_companies", tuple()),
        ("update_companies", tuple()),
        (
            "search_index",
            (
                "--models companies",
                "--populate",
                "--no-count",
            ),
        ),
    ]

    def handle(self, *args, **options):
        for scraper, args in self.commands:
            try:
                management.call_command(scraper, *args)
            except Exception:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
