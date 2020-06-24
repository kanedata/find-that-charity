from django.core import management
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    scrapers = [
        "ccew",
        "ccni",
        "oscr",
    ]

    def handle(self, *args, **options):
        for scraper in self.scrapers:
            management.call_command("import_{}".format(scraper))
        management.call_command("update_orgids")
