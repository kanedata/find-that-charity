import unittest

from django.urls import reverse

import ftc.tests
from findthatcharity.utils import (
    list_to_string,
    to_titlecase,
    format_currency,
    get_domain,
    str_format,
    normalise_name,
    number_format,
    regex_search,
)


class TestUtils(unittest.TestCase):
    def test_to_titlecase(self):
        names = (
            ("THE CHARITY THE NAME", "The Charity the Name"),
            ("CHARITY UK LTD", "Charity UK Ltd"),
            ("BCDF", "BCDF"),
            ("MRS SMITH", "Mrs Smith"),
            ("1ST SCOUT GROUP", "1st Scout Group"),
            ("SCOUT 345TH GROUP", "Scout 345th Group"),
            ("THE CHARITY (THE NAME)", "The Charity (the Name)"),
            (12345, 12345),
            ("THE CHARITY (the name)", "THE CHARITY (the name)"),
            ("Charity UK Ltd", "Charity UK Ltd"),
            ("charity uk ltd", "Charity UK Ltd"),
            ("CHARITY'S SHOP UK LTD", "Charity's Shop UK Ltd"),
            ("CHARITY'S YOU'RE SHOP UK LTD", "Charity's You're Shop UK Ltd"),
        )
        for n1, n2 in names:
            self.assertEqual(to_titlecase(n1), n2)

        sentences = (
            ("the charity the name", "The charity the name"),
            (
                "the charity the name. another sentence goes here.",
                "The charity the name. Another sentence goes here.",
            ),
            # (
            #     "the charity the name. another sentence goes here i should think.",
            #     "The charity the name. Another sentence goes here I should think.",
            # ),
        )
        for s1, s2 in sentences:
            self.assertEqual(to_titlecase(s1, sentence=True), s2)

    def test_list_to_string(self):
        lists = (
            ("item1", "item1"),
            (set(["item1"]), "item1"),
            (["item1"], "item1"),
            (["item1", "item2"], "item1 and item2"),
            (["item1", "item2", "item3"], "item1, item2 and item3"),
        )
        for l1, l2 in lists:
            self.assertEqual(list_to_string(l1), l2)
        self.assertEqual(
            list_to_string(["item1", "item2", "item3"], sep="; "),
            "item1; item2 and item3",
        )
        self.assertEqual(
            list_to_string(["item1", "item2", "item3"], final_sep=" et "),
            "item1, item2 et item3",
        )
        self.assertEqual(
            list_to_string(["item1", "item2", "item3"], sep="; ", final_sep=" et "),
            "item1; item2 et item3",
        )

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

    def test_regex_search(self):
        self.assertTrue(regex_search("test", "test"))
        self.assertTrue(regex_search("1234", "[0-9]+"))
        self.assertFalse(regex_search("test", "1234"))

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
        self.assertContains(response["content-type"], "text/csv")
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
