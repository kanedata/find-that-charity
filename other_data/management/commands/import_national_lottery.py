import csv
import datetime
import io
from urllib.parse import urlencode

from django.db.models.functions import ExtractMonth, ExtractYear

from ftc.management.commands._base_scraper import CSVScraper
from other_data.models import Grant

NL_API_URL = "https://nationallottery.dcms.gov.uk/api/v1/grants/csv-export/"


class Command(CSVScraper):
    name = "nldcms"
    start_urls = [NL_API_URL]
    float_fields = [
        "Amount Awarded",
    ]
    encoding = "utf-8-sig"
    date_fields = ["Award Date", "Last Modified"]
    date_format = {
        "Award Date": "%Y-%m-%d",
        "Last Modified": "%Y-%m-%d %H:%M:%S",
    }
    source = {
        "title": "National Lottery grants",
        "description": "The National Lottery grant database brings together National Lottery grant data from the launch of the National Lottery in 1994 to the present. The data is uploaded periodically onto this database by the 12 National Lottery Distributing Bodies. Data on this website is not considered official statistics.",
        "identifier": "nldcms",
        "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Department for Culture, Media and Sport",
            "website": "https://nationallottery.dcms.gov.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://nationallottery.dcms.gov.uk/",
                "title": "National Lottery Grant Database",
            }
        ],
    }
    models_to_delete = [Grant]

    def _get_existing_grants(self):
        grants_to_match = Grant.objects.filter(
            fundingOrganization_type="Lottery Distributor"
        ).exclude(
            spider=self.name,
        )

        self.existing_grants = set(grants_to_match.values_list("grant_id", flat=True))
        self.logger.info(
            "Selected {} existing grant ids".format(len(self.existing_grants))
        )

        # Grants are excluded as duplicates if they have the same values
        # across the following fields
        self.grant_matcher = set(
            grants_to_match.values_list(
                "title",
                "amountAwarded",
                ExtractYear("awardDate"),
                ExtractMonth("awardDate"),
                "recipientOrganization_name",
                "fundingOrganization_id",
            )
        )
        self.logger.info(
            "Selected {} existing grant matches".format(len(self.grant_matcher))
        )

    def fetch_file(self):
        self._get_existing_grants()
        self.files = {}
        u = self.start_urls[0]
        self.set_download_url(u)
        initial_year = 1994
        current_year = datetime.datetime.now().year
        for year in range(initial_year, current_year + 1):
            url = (
                u
                + "?"
                + urlencode(
                    {
                        "page": 1,
                        "limit": 10,
                        "ordering": "-award_date",
                        "good_cause_area": "",
                        "funding_org": "",
                        "region": "",
                        "local_authority": "",
                        "uk_constituency": "",
                        "ward": "",
                        "recipient_org": "",
                        "award_date_after": f"{year}-01-01",
                        "award_date_before": f"{year}-12-31",
                        "amount_awarded_min": "",
                        "amount_awarded_max": "",
                        "search": "",
                    }
                )
            )
            r = self.session.get(url)
            r.raise_for_status()
            self.files[url] = r

    def parse_file(self, response, source_url):
        csv_text = response.content.decode(self.encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(a)
            for k, row in enumerate(csvreader):
                self.parse_row(row)

    def parse_row(self, original_row):
        row = self.clean_fields(original_row)

        # check for duplicate grants
        if (
            row["Identifier"].replace("DCMS-tnlcomfund-", "360G-tnlcomfund-")
            in self.existing_grants
        ):
            return None

        matching_field = (
            row["Title"],
            row["Amount Awarded"],
            row["Award Date"].year,
            row["Award Date"].month,
            row["Recipient Org:Name"],
            row["Funding Org:Identifier"],
        )
        if matching_field in self.grant_matcher:
            return None

        grant = dict(
            grant_id=row["Identifier"],
            title=row["Title"],
            description=row["Description"],
            currency=row["Currency"],
            amountAwarded=row["Amount Awarded"],
            awardDate=row["Award Date"],
            recipientOrganization_id=row["Recipient Org:Identifier"],
            recipientOrganization_name=row["Recipient Org:Name"],
            recipient_type=Grant.RecipientType.ORGANISATION,
            fundingOrganization_id=row["Funding Org:Identifier"],
            fundingOrganization_name=row["Funding Org:Name"],
            fundingOrganization_type="Lottery Distributor",
            publisher_prefix="dcms-nationallottery",
            publisher_name="The National Lottery",
            license="http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
            scrape=self.scrape,
            spider=self.name,
        )

        # check for grants to individuals
        if (
            grant["recipientOrganization_name"].strip()
            in ("Grant to Individual", "Grant Awarded to Individual")
        ) or (grant["description"].strip() in ("Athlete Performance Award",)):
            grant["recipient_type"] = Grant.RecipientType.INDIVIDUAL
            grant["recipientIndividual_id"] = grant["recipientOrganization_id"]
            grant["recipientIndividual_name"] = grant["recipientOrganization_name"]
            del grant["recipientOrganization_id"]
            del grant["recipientOrganization_name"]

        self.add_record(Grant, grant)
