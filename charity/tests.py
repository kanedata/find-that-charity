from django.urls import reverse

from ftc.tests import TestCase


class CharityViewTests(TestCase):
    def test_charity(self):

        response = self.client.get(
            reverse("charity_html", kwargs={"regno": "1234"}), follow=True
        )
        self.assertRedirects(
            response, "/orgid/GB-CHC-1234", status_code=301, target_status_code=200
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Source publisher", html=True)
        self.assertContains(response, "Registered Charity", html=True)
        self.assertContains(response, "Test organisation", html=True)
        self.assertContains(response, "Test description", html=True)

    def test_organisation_404(self):

        response = self.client.get(
            reverse("charity_html", kwargs={"regno": "3456"}), follow=True
        )
        self.assertRedirects(
            response, "/orgid/GB-CHC-3456", status_code=301, target_status_code=404
        )
        self.assertEqual(response.status_code, 404)
