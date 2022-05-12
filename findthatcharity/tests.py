import unittest

from django.urls import reverse

import ftc.tests
from findthatcharity.utils import list_to_string, to_titlecase


class TestUtils(unittest.TestCase):
    def test_to_titlecase(self):
        names = (
            ("THE CHARITY THE NAME", "The Charity the Name"),
            ("CHARITY UK LTD", "Charity UK Ltd"),
            ("BCDF", "BCDF"),
            ("MRS SMITH", "Mrs Smith"),
            ("THE CHARITY (THE NAME)", "The Charity (the Name)"),
        )
        for n1, n2 in names:
            assert to_titlecase(n1) == n2

    def test_list_to_string(self):
        lists = (
            (["item1"], "item1"),
            (["item1", "item2"], "item1 and item2"),
            (["item1", "item2", "item3"], "item1, item2 and item3"),
        )
        for l1, l2 in lists:
            assert list_to_string(l1) == l2
        assert (
            list_to_string(["item1", "item2", "item3"], sep="; ")
            == "item1; item2 and item3"
        )
        assert (
            list_to_string(["item1", "item2", "item3"], final_sep=" et ")
            == "item1, item2 et item3"
        )
        assert (
            list_to_string(["item1", "item2", "item3"], sep="; ", final_sep=" et ")
            == "item1; item2 et item3"
        )


class IndexViewTests(ftc.tests.TestCase):
    def test_index(self):

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "contains information about 1 ")
        self.assertContains(response, "Registered Charity (England and Wales)")
        self.assertContains(response, "Source publisher")

    def test_about(self):

        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Source publisher", html=True)


class TestClacks(ftc.tests.TestCase):
    def test_xheader_exists(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response["X-Clacks-Overhead"], "GNU Terry Pratchett")
