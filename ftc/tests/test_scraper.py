import os

import requests_mock
from django.test import TestCase

from ftc.management.commands._base_scraper import BaseScraper
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


class BaseScraperTests(TestCase):
    def test_parse_company_number(self):
        BaseScraper.name = "test"
        scraper = BaseScraper()
        company_numbers = [
            ("1234", "00001234"),
            ("", None),
            ("000", None),
            ("01234567", None),
            ("12345678", None),
            ("SC123", "SC123"),
            ("00001234", "00001234"),
            ("SC001234", "SC001234"),
            ("19191919", "19191919"),
            ("1919191919", "1919191919"),
        ]
        for number, expected in company_numbers:
            self.assertEqual(scraper.parse_company_number(number), expected)

    def test_org_id(self):
        BaseScraper.name = "test"
        scraper = BaseScraper()
        scraper.org_id_prefix = "XI-TEST"
        scraper.id_field = "id"
        org_ids = [
            ("00001234", "XI-TEST-00001234"),
            ("SC123", "XI-TEST-SC123"),
        ]
        for url, expected in org_ids:
            self.assertEqual(scraper.get_org_id({"id": url}), expected)


class ScraperTests(TestCase):
    def mock_csv_downloads(self, m):
        dirname = os.path.dirname(__file__)
        for url, filename in MOCK_FILES:
            with open(os.path.join(dirname, "fixtures", filename), "rb") as a:
                m.get(url, content=a.read())


class CASCCommandTests(ScraperTests):
    def test_casc_scraper(self):
        with requests_mock.Mocker() as m:
            self.mock_csv_downloads(m)
            scraper = CASCCommand()
            scraper.handle()


class RORCommandTests(ScraperTests):
    def test_ror_scraper(self):
        with requests_mock.Mocker() as m:
            self.mock_csv_downloads(m)
            scraper = RORCommand()
            scraper.handle()

    def test_org_id(self):
        scraper = RORCommand()
        org_ids = [
            ("https://ror.org/00001234", "XI-ROR-00001234"),
            ("https://ror.org/SC123", "XI-ROR-SC123"),
        ]
        for url, expected in org_ids:
            self.assertEqual(scraper.get_org_id({"id": url}), expected)
