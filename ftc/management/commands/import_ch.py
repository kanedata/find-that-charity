import argparse

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    commands = [
        ("import_companies", tuple()),
        ("update_companies", tuple()),
        (
            "search_index",
            (
                "--populate",
                "--models",
                "companies.company",
                "--no-count",
            ),
        ),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--debug",
            action=argparse.BooleanOptionalAction,
            help="Debug",
            default=settings.DEBUG,
        )

    def handle(self, *args, **options):
        for scraper, command_args in self.commands:
            if scraper == "import_companies":
                if options["debug"]:
                    command_args += ("--debug",)
                else:
                    command_args += ("--no-debug",)
            try:
                self.stdout.write(
                    "Running {} {}".format(scraper, " ".join(command_args))
                )
                management.call_command(scraper, *command_args)
            except Exception as e:
                self.stdout.write(self.style.ERROR("Command {} failed".format(scraper)))
                self.stdout.write(self.style.ERROR(e))
