import unittest

from django.urls import reverse

import ftc.tests
from findthatcharity.utils import (
    format_currency,
    get_domain,
    normalise_name,
    number_format,
    str_format,
)


class TestUtils(unittest.TestCase):
    def test_format_currency(self):
        items = (
            (12345, "£12,345", {}),
            (12345, "£12,345", {"currency": "GBP"}),
            (12345, "US$12,345", {"currency": "USD"}),
            (12345, "€12345", {"currency": "EUR", "int_format": "¤###0"}),
        )
        for amount, formatted, kwargs in items:
            self.assertEqual(format_currency(amount, **kwargs), formatted)

    def test_get_domain(self):
        items = (
            ("http://www.google.com", "google.com"),
            ("example.com", "example.com"),
            ("example.com/blahblahblah", "example.com"),
            ("http://example.com/blahblahblah", "example.com"),
            ("http://www.example.com/blahblahblah", "example.com"),
            ("https://www.example.com/blahblahblah", "example.com"),
            ("https://www.gmail.com/blahblahblah", None),
            ("", None),
            ("http://username:pass[word@localhost:6379/0", None),
        )
        for url, domain in items:
            with self.subTest(url=url, domain=domain):
                self.assertEqual(get_domain(url), domain)

    def test_normalise_name(self):
        items = (
            ("The Charity the Name", "charity name"),
            ("The Charity the Name Limited", "charity name"),
            ("The Charity           Name Limited", "charity name"),
        )
        for name, normalised in items:
            self.assertEqual(normalise_name(name), normalised)

    def test_str_format(self):
        self.assertEqual(str_format("test", "[{}]"), "[test]")
        self.assertEqual(str_format(1234, "[{:,.0f}]"), "[1,234]")

    def test_number_format(self):
        items = (
            (None, "-", {}),
            (0, "-", {}),
            (0, "-", {"scale": 1000}),
            (1000, "1,000", {"scale": 1}),
            (-1000, "(1,000)", {"scale": 1}),
            (45_123, "45.1", {"scale": 1000}),
            (-45_123, "(45.1)", {"scale": 1000}),
        )
        for amount, formatted, kwargs in items:
            self.assertEqual(number_format(amount, **kwargs), formatted)


class IndexViewTests(ftc.tests.TestCase):
    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "contains information about 3 ")
        self.assertContains(response, "Registered Charity (England and Wales)")
        self.assertContains(response, "Source publisher")

    def test_index_search(self):
        response = self.client.get(reverse("index") + "?q=organisation")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Search Results")

    def test_index_search_csv(self):
        response = self.client.get(reverse("index") + "?q=organisation&filetype=csv")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/csv" in response["content-type"])
        self.assertContains(response, "name")

    def test_about(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Source publisher", html=True)


class TestClacks(ftc.tests.TestCase):
    def test_xheader_exists(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response["X-Clacks-Overhead"], "GNU Terry Pratchett")
