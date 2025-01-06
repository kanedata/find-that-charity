import json
import logging
import os

from ftc.tests import TestCase

logger = logging.getLogger(__name__)

with open(
    os.path.join(os.path.dirname(__file__), "data", "random_organisation_response.json")
) as f:
    RANDOM_ORG_RESPONSE = json.load(f)


class TestOrganisationAPI(TestCase):
    # GET request to /api/v1/organisation/__id__ should return an organisation
    def test_get_organisation(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-1234")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["description"], "Test description")

    def test_get_organisation_slash(self):
        response = self.client.get("/api/v1/organisations/GB-EDU-123/ABC")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["description"], "Test description")

    def test_get_organisationmissing(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-BLAHBLAH")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error"], "No Organisation found.")

    def test_get_random_organisation(self):
        self.mock_es.return_value.search.return_value = RANDOM_ORG_RESPONSE

        response = self.client.get("/api/v1/organisations/_random")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["description"], "Test description")

    def test_get_canonical_organisation(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-6/canonical")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["id"], "GB-CHC-5")

    def test_get_canonical_organisation_same(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-5/canonical")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["id"], "GB-CHC-5")

    def test_get_canonical_organisation_with_slash(self):
        response = self.client.get("/api/v1/organisations/GB-EDU-123/ABC/canonical")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["id"], "GB-CHC-5")

    def test_get_canonical_organisation_single(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-1234/canonical")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["result"]["organisationTypePrimary"]["title"], "Registered Charity"
        )
        self.assertEqual(data["result"]["id"], "GB-CHC-1234")

    def test_get_linked_organisations(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-5/linked")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["count"], len(data["result"]))
        self.assertEqual(data["result"][0]["name"], "Test organisation 2")

    def test_get_organisation_source(self):
        response = self.client.get("/api/v1/organisations/GB-CHC-1234/source")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"]["publisher"], "Source publisher")

    def test_filter_organisations(self):
        response = self.client.get("/api/v1/organisations?active=true")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["result"]), 4)
        ids = sorted([x["id"] for x in data["result"]])
        self.assertEqual(ids, ["GB-CHC-1234", "GB-CHC-5", "GB-CHC-6", "GB-EDU-123/ABC"])
