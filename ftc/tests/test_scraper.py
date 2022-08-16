import os

import requests_mock
from django.test import TestCase

from ftc.management.commands.import_casc import Command as CASCCommand
from ftc.management.commands.import_ror import Command as RORCommand


MOCK_FILES = (
    (
        "https://zenodo.org/api/records/?communities=ror-data&sort=mostrecent",
        "ror.json",
    ),
    (
        "https://zenodo.org/api/files/25d4f93f-6854-4dd4-9954-173197e7fad7/v1.1-2022-06-16-ror-data.zip",
        "ror-data.zip",
    ),
    (
        "https://raw.githubusercontent.com/ThreeSixtyGiving/cascs/master/cascs.csv",
        "cascs.csv",
    ),
    (
        "https://raw.githubusercontent.com/ThreeSixtyGiving/cascs/master/casc_company_house.csv",
        "casc_company_house.csv",
    ),
)


class ScraperTests(TestCase):
    def mock_csv_downloads(self, m):
        dirname = os.path.dirname(__file__)
        for url, filename in MOCK_FILES:
            with open(os.path.join(dirname, "fixtures", filename), "rb") as a:
                m.get(url, content=a.read())

    def test_casc_scraper(self):
        with requests_mock.Mocker() as m:
            self.mock_csv_downloads(m)
            scraper = CASCCommand()
            scraper.handle()

    def test_ror_scraper(self):
        with requests_mock.Mocker() as m:
            self.mock_csv_downloads(m)
            scraper = RORCommand()
            scraper.handle()
