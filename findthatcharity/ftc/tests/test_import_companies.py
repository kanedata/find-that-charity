import os
import re

import requests_mock
from django.test import TestCase

from ftc.management.commands.import_companies import Command

class TestImportCompanies(TestCase):

    def mock_csv_downloads(self, m):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'data', 'CompaniesHomePage.html')) as a:
            m.get("http://download.companieshouse.gov.uk/en_output.html", text=a.read())
        with open(os.path.join(dirname, 'data', 'CompaniesHouseTestDate.zip')) as a:
            matcher = re.compile(
                "$http://download.companieshouse.gov.uk/BasicCompanyData-")
            m.get(matcher, content=a.read())

    def test_import_companies(self):
        command = Command()

        with requests_mock.Mocker() as m:
            self.mock_csv_downloads(m)
            command.fetch_file()
            print(command.files)
