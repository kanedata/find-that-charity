import logging

from charity_django.companies.models import Company

from ftc.tests import TestCase

logger = logging.getLogger(__name__)


class TestCompanyAPI(TestCase):
    def setUp(self):
        super().setUp()
        Company.objects.create(
            CompanyNumber="12345678",
            CompanyName="Test organisation",
        )

    # GET request to /api/v1/companies/__id__ should return an organisation
    def test_get_companies(self):
        response = self.client.get("/api/v1/companies/12345678")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"]["CompanyName"], "Test organisation")

    def test_get_company_missing(self):
        response = self.client.get("/api/v1/companies/BLAHBLAH")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error"], "No Company matches the given query.")
