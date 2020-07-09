import os
import re
from unittest import TestCase

import requests_mock

from ftc.documents import FullOrganisation
from ftc.models import Organisation

# from django.test import TestCase


class TestDocuments(TestCase):
    
    def test_fullorganisation_sortname(self):
        names = (
            ('the charity the name', 'charity the name'),
            ('charity the name', 'charity the name'),
            (' the charity the name', 'charity the name'),
            ('the  charity the name', 'charity the name'),
            ("' charity the name'", 'charity the name'),
            ("'  charity the name'", 'charity the name'),
            (' charity the name', 'charity the name'),
            ('(2charity the name', '2charity the name'),
            ('Above Us Only Sky?', 'above us only sky'),
        )
        for n1, n2 in names:
            o = Organisation(name=n1)
            d = FullOrganisation()
            assert d.prepare_sortname(o) == n2
