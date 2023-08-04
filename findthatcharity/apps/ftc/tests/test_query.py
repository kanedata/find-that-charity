from django.shortcuts import Http404

from findthatcharity.apps.ftc.query import (
    OrganisationSearch,
    get_linked_organisations,
    get_organisation,
)
from findthatcharity.apps.ftc.tests import TestCase


class QueryTests(TestCase):
    def test_get_organisation(self):
        org = get_organisation("GB-CHC-1234")
        self.assertEqual(org.name, "Test organisation")

    def test_get_organisations(self):
        org = get_organisation("GB-CHC-5")
        self.assertEqual(org.name, "Test organisation 2")

    def test_get_organisation_404(self):
        with self.assertRaises(Http404):
            get_organisation("XX-XXX-3456")

    def test_get_linked_organisation(self):
        org = get_linked_organisations("GB-CHC-1234")
        self.assertEqual(org.name, "Test organisation")
        self.assertEqual(len(org.records), 1)

    def test_get_linked_organisations(self):
        org = get_linked_organisations("GB-CHC-5")
        self.assertEqual(org.name, "Test organisation 2")
        self.assertEqual(len(org.records), 2)

    def test_get_linked_organisations_404(self):
        with self.assertRaises(Http404):
            get_linked_organisations("XX-XXX-3456")

    def test_organisation_search(self):
        s = OrganisationSearch()
        self.assertIsNone(s.term)

    def test_organisation_search_set_criteria(self):
        s = OrganisationSearch()
        self.assertIsNone(s.term)
