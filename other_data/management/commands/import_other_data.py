from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    scrapers = [
        "gender_pay_gap",
        "360giving",
        "national_lottery",
        "cqc",
        "wikidata",
    ]

    def handle(self, *args, **options):
        for scraper in self.scrapers:
            try:
                management.call_command("import_{}".format(scraper))
            except Exception:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
