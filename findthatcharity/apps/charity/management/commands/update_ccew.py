import re

from findthatcharity.apps.charity.management.commands._ccew_sql import UPDATE_CCEW
from findthatcharity.apps.ftc.management.commands._base_scraper import BaseScraper
from findthatcharity.apps.ftc.models import (
    Organisation,
    OrganisationClassification,
    OrganisationLink,
    Scrape,
)


class Command(BaseScraper):
    name = "ccew"
    allowed_domains = ["charitycommission.gov.uk"]
    start_urls = []
    encoding = "cp858"
    org_id_prefix = "GB-CHC"
    id_field = "regno"
    date_fields = []
    date_format = "%Y-%m-%d %H:%M:%S"
    zip_regex = re.compile(r".*/RegPlusExtract.*?\.zip.*?")
    base_url = "https://ccewuksprdoneregsadata1.blob.core.windows.net/data/txt/publicextract.{}.zip"
    source = {
        "title": "Registered charities in England and Wales",
        "description": "Data download service provided by the Charity Commission",
        "identifier": "ccew",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
        "license_name": "Open Government Licence v2.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Charity Commission for England and Wales",
            "website": "https://www.gov.uk/charity-commission",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://register-of-charities.charitycommission.gov.uk/register/full-register-download",
                "title": "Registered charities in England and Wales",
            }
        ],
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (England and Wales)",
        "Registered Company",
        "Incorporated Charity",
        "Charitable Incorporated Organisation",
        "Charitable Incorporated Organisation - Association",
        "Charitable Incorporated Organisation - Foundation",
        "Trust",
    ]

    def close_spider(self):
        # execute SQL statements
        self.execute_sql_statements(UPDATE_CCEW)

        self.object_count = Organisation.objects.filter(
            spider__exact=self.name,
            scrape_id=self.scrape.id,
        ).count()
        self.scrape.items = self.object_count
        results = {"records": self.object_count}
        self.logger.info("Saved {:,.0f} organisation records".format(self.object_count))

        link_records_count = OrganisationLink.objects.filter(
            spider__exact=self.name,
            scrape_id=self.scrape.id,
        ).count()
        if link_records_count:
            results["link_records"] = link_records_count
            self.object_count += results["link_records"]
            self.logger.info(
                "Saved {:,.0f} link records".format(results["link_records"])
            )

        self.scrape.errors = self.error_count
        self.scrape.result = results
        if self.object_count == 0:
            self.scrape.status = Scrape.ScrapeStatus.FAILED
        elif self.error_count > 0:
            self.scrape.status = Scrape.ScrapeStatus.ERRORS
        else:
            self.scrape.status = Scrape.ScrapeStatus.SUCCESS
        self.scrape.save()

        # if we've been successfull then delete previous items
        if self.object_count > 0:
            self.logger.info("Deleting previous records")
            Organisation.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            OrganisationLink.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            OrganisationClassification.objects.filter(
                spider__exact=self.name,
            ).exclude(
                scrape_id=self.scrape.id,
            ).delete()
            self.logger.info("Deleted previous records")
