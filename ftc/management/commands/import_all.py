from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    scrapers = [
        "casc",
        "gor",
        "grid",
        "hesa",
        "lae",
        "lani",
        "las",
        "manual_links",
        "mutuals",
        "nhsods",
        "pla",
        "rsl",
        "schools_gias",
        "schools_ni",
        "schools_scotland",
        "schools_wales",
    ]

    def handle(self, *args, **options):
        scrapers_to_run = ["import_{}".format(scraper) for scraper in self.scrapers] + [
            "update_orgids",
            "update_geodata",
        ]
        for scraper in scrapers_to_run:
            try:
                management.call_command("import_{}".format(scraper))
            except Exception:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
