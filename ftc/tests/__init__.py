import datetime
from unittest.mock import patch

import django.test
from django.utils import timezone

from ftc.models import Organisation, OrganisationType, Scrape, Source


class TestCase(django.test.TestCase):
    databases = {"data", "admin"}

    def setUp(self):
        # setup elasticsearch patcher
        self.es_patcher = patch("ftc.documents.get_connection")
        self.addCleanup(self.es_patcher.stop)
        self.mock_es = self.es_patcher.start()

        ot = OrganisationType.objects.create(title="Registered Charity")
        ot2 = OrganisationType.objects.create(
            title="Registered Charity (England and Wales)"
        )
        s = Source.objects.create(
            id="ts",
            data={
                "title": "Test source",
                "publisher": {
                    "name": "Source publisher",
                },
            },
        )
        scrape = Scrape.objects.create(
            status=Scrape.ScrapeStatus.SUCCESS,
            spider="test",
            errors=0,
            items=1,
            log="",
            start_time=timezone.now() - datetime.timedelta(minutes=10),
            finish_time=timezone.now() - datetime.timedelta(minutes=5),
        )
        Organisation.objects.create(
            org_id="GB-CHC-1234",
            orgIDs=["GB-CHC-1234"],
            linked_orgs=["GB-CHC-1234"],
            description="Test description",
            name="Test organisation",
            active=True,
            organisationTypePrimary=ot,
            source=s,
            scrape=scrape,
            organisationType=[ot.slug, ot2.slug],
        )
        Organisation.objects.create(
            org_id="GB-CHC-5",
            orgIDs=["GB-CHC-5", "GB-CHC-6"],
            linked_orgs=["GB-CHC-5", "GB-CHC-6"],
            description="Test description",
            name="Test organisation 2",
            active=True,
            organisationTypePrimary=ot,
            source=s,
            scrape=scrape,
            organisationType=[ot.slug, ot2.slug],
        )
        Organisation.objects.create(
            org_id="GB-CHC-6",
            orgIDs=["GB-CHC-5", "GB-CHC-6"],
            linked_orgs=["GB-CHC-5", "GB-CHC-6"],
            description="Test description",
            name="Test organisation 3",
            active=True,
            organisationTypePrimary=ot,
            source=s,
            scrape=scrape,
            organisationType=[ot.slug, ot2.slug],
        )
