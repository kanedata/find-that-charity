import logging

from charity.models import Charity
from ftc.tests import TestCase

logger = logging.getLogger(__name__)


class TestCharityAPI(TestCase):
    def setUp(self):
        super().setUp()
        Charity.objects.create(
            id="GB-CHC-1234567",
            name="Test charity",
            active=True,
            scrape=self.scrape,
        )
        charity2 = Charity.objects.create(
            id="GB-CHC-2345678",
            name="Test charity 2",
            active=True,
            scrape=self.scrape,
        )
        charity2.financial.create(
            income=123456,
            spending=123456,
            fyend="2020-03-31",
        )
        charity2.financial.create(
            income=654321,
            spending=123456,
            fyend="2019-03-31",
        )

    # GET request to /api/v1/companies/__id__ should return an organisation
    def test_get_charity(self):
        response = self.client.get("/api/v1/charities/1234567")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"]["name"], "Test charity")

    def test_get_charity_missing(self):
        response = self.client.get("/api/v1/charities/BLAHBLAH")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error"], "No Charity matches the given query.")

    def test_get_charity_financial_latest(self):
        response = self.client.get("/api/v1/charities/2345678/financial/latest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"]["income"], 123456)
        self.assertEqual(data["result"]["fyend"], "2020-03-31")

    def test_get_charity_financial_date(self):
        response = self.client.get("/api/v1/charities/2345678/financial/2019-03-31")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"]["income"], 654321)
        self.assertEqual(data["result"]["fyend"], "2019-03-31")

    def test_get_charity_financial_missing(self):
        urls = [
            "/api/v1/charities/2345678/financial/2018-03-31",
            "/api/v1/charities/2345678/financial/2020-05-15",
            "/api/v1/charities/1234567/financial/latest",
            "/api/v1/charities/1234567/financial/2018-03-31",
            "/api/v1/charities/1234567/financial/2020-05-15",
            "/api/v1/charities/1234567/financial/2020-03-31",
            "/api/v1/charities/blahblah/financial/latest",
            "/api/v1/charities/blahblah/financial/2018-03-31",
            "/api/v1/charities/blahblah/financial/2020-05-15",
            "/api/v1/charities/blahblah/financial/2020-03-31",
        ]
        for url in urls:
            with self.subTest(url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)
                data = response.json()
                self.assertTrue(
                    data["error"]
                    in [
                        "No CharityFinancial matches the given query.",
                        "No Charity matches the given query.",
                    ]
                )
