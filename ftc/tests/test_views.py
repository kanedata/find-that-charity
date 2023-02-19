from django.urls import reverse

from ftc.tests import TestCase


class OrganisationViewTests(TestCase):
    def test_organisation(self):
        response = self.client.get(
            reverse("orgid_html", kwargs={"org_id": "GB-CHC-1234"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Source publisher", html=True)
        self.assertContains(response, "Registered Charity", html=True)
        self.assertContains(response, "Test organisation", html=True)
        self.assertContains(response, "Test description", html=True)

    def test_organisation_json(self):
        response = self.client.get(
            reverse("orgid_json", kwargs={"org_id": "GB-CHC-1234"})
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["name"], "Test organisation")
        self.assertEqual(response_json["id"], "GB-CHC-1234")
        self.assertEqual(response_json["latestIncome"], None)
        self.assertEqual(response_json["latestEmployees"], None)

    def test_organisation_404(self):
        response = self.client.get(
            reverse("orgid_html", kwargs={"org_id": "XX-XXX-3456"})
        )
        self.assertEqual(response.status_code, 404)

    def test_organisation_json_404(self):
        response = self.client.get(
            reverse("orgid_json", kwargs={"org_id": "XX-XXX-3456"})
        )
        self.assertEqual(response.status_code, 404)
