from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    scrapers = [
        "casc",
        "gor",
        "ror",
        "hesa",
        "import_la_mysociety",
        # "lae",
        # "lani",
        # "las",
        # "pla",
        "manual_links",
        "mutuals",
        "nhsods",
        "rsl",
        "schools_gias",
        "schools_scotland",
        "schools_wales",
        # "schools_ni",
    ]

    def handle(self, *args, **options):
        scrapers_to_run = ["import_{}".format(scraper) for scraper in self.scrapers]
        for scraper in scrapers_to_run:
            try:
                management.call_command(scraper)
            except Exception:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
