from django.core import management
from django.core.management.base import BaseCommand, CommandError


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
        "nhsods",
        "pla",
        "rsl",
        "schools_gias",
        "schools_ni",
        "schools_scotland",
        "schools_wales",
    ]

    def handle(self, *args, **options):
        for scraper in self.scrapers:
            management.call_command("import_{}".format(scraper))
        management.call_command("update_orgids")
