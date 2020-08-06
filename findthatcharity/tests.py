import unittest
import datetime

import django.test
from django.urls import reverse
from django.utils import timezone

from findthatcharity.utils import to_titlecase, list_to_string
from ftc.models import Organisation, Source, OrganisationType, Scrape


class TestUtils(unittest.TestCase):

    def test_to_titlecase(self):
        names = (
            ('THE CHARITY THE NAME', 'The Charity the Name'),
            ('CHARITY UK LTD', 'Charity UK Ltd'),
            ('BCDF', 'BCDF'),
            ('MRS SMITH', 'Mrs Smith'),
            ("THE CHARITY (THE NAME)", 'The Charity (the Name)'),
        )
        for n1, n2 in names:
            assert to_titlecase(n1) == n2

    def test_list_to_string(self):
        lists = (
            (['item1'], 'item1'),
            (['item1', 'item2'], 'item1 and item2'),
            (['item1', 'item2', 'item3'], 'item1, item2 and item3'),
        )
        for l1, l2 in lists:
            assert list_to_string(l1) == l2
        assert list_to_string(['item1', 'item2', 'item3'], sep="; ") == 'item1; item2 and item3'
        assert list_to_string(['item1', 'item2', 'item3'],
                              final_sep=" et ") == 'item1, item2 et item3'
        assert list_to_string(['item1', 'item2', 'item3'],
                              sep="; ", final_sep=" et ") == 'item1; item2 et item3'


class IndexViewTests(django.test.TestCase):

    def setUp(self):
        ot = OrganisationType.objects.create(title='Registered Charity')
        ot2 = OrganisationType.objects.create(title='Registered Charity (England and Wales)')
        s = Source.objects.create(id="ts", data={
            "title": "Test source",
            "publisher": {
                "name": "Source publisher",
            }
        })
        scrape = Scrape.objects.create(
            status=Scrape.ScrapeStatus.SUCCESS,
            spider='test',
            errors=0,
            items=1,
            log="",
            start_time=timezone.now() - datetime.timedelta(minutes=10),
            finish_time=timezone.now() - datetime.timedelta(minutes=5),
        )
        Organisation.objects.create(
            org_id='XX-XXX-1234',
            description='Test description',
            name='Test organisation',
            active=True,
            organisationTypePrimary=ot,
            source=s,
            scrape=scrape,
            organisationType=[ot.slug, ot2.slug],
        )

    def test_index(self):

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "contains information about 1 ")
        self.assertContains(response, "Registered Charity (England and Wales)")
        self.assertContains(response, "Source Publisher")

    def test_about(self):

        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Find that Charity", html=True)
        self.assertContains(response, "Source publisher", html=True)
