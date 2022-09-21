from unittest import TestCase

from ftc.documents import OrganisationGroup
from ftc.models import Organisation

# from django.test import TestCase


class TestDocuments(TestCase):
    def test_fullorganisation_sortname(self):
        names = (
            ("the charity the name", "charity name"),
            ("charity the name", "charity name"),
            (" the charity the name", "charity name"),
            ("the  charity the name", "charity name"),
            ("' charity the name'", "charity name"),
            ("'  charity the name'", "charity name"),
            ("-  charity the name'", "charity name"),
            (" charity the name", "charity name"),
            ("(2charity the name", "2charity name"),
            ("1st borough scouts", "1st borough scouts"),
            ("Above Us Only Sky?", "above us only sky"),
        )
        for n1, n2 in names:
            o = Organisation(name=n1)
            d = OrganisationGroup()
            with self.subTest(n1=n1, n2=n2):
                assert d.prepare_sortname(o) == n2
