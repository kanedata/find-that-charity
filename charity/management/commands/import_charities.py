from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    scrapers = [
        "ccni",
        # "oscr",
        "ccew",
    ]

    def handle(self, *args, **options):
        for scraper in self.scrapers:
            try:
                management.call_command("import_{}".format(scraper))
            except Exception:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
        management.call_command("import_ukcat")
        management.call_command("calculate_scale")
        management.call_command("import_names")
