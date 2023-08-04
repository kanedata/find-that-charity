import csv
import io
from urllib.parse import urlparse

from other_data.models import GenderPayGap

from findthatcharity.apps.ftc.management.commands._base_scraper import HTMLScraper

EXCLUDE_ADDRESS = [
    "amazonaws.com",
    "bit.ly",
    "indd.adobe.com",
    "drive.google.com",
    "docs.google.com",
    "s27.q4cdn.com",
    "eur01.safelinks.protection.outlook.com",
    "culinaintranet",
    "wixstatic.com",
    "cdn-website.com",
    "assets.ctfassets.net",
    "kc-usercontent.com",
]

UPDATE_WEBSITES = """
    with latest_gpg as (
        select "EmployerId", max("Year") as "Year"
        from other_data_genderpaygap gpg
        where "CompanyWebsite" is not null
        group by "EmployerId"
    )
    update ftc_organisation
    set url = gpg."CompanyWebsite"
    from ftc_organisation fo
        inner join other_data_genderpaygap gpg
            on fo.org_id = gpg.org_id
        inner join latest_gpg
            on gpg."Year" = latest_gpg."Year"
                and gpg."EmployerId" = latest_gpg."EmployerId"
    where ftc_organisation.id = fo.id
    and fo.url is null
    and gpg."CompanyWebsite" is not null;
"""


class Command(HTMLScraper):
    name = "gpg"
    allowed_domains = ["gender-pay-gap.service.gov.uk"]
    start_urls = [
        "https://gender-pay-gap.service.gov.uk/viewing/download",
    ]
    float_fields = [
        "DiffMeanHourlyPercent",
        "DiffMedianHourlyPercent",
        "DiffMeanBonusPercent",
        "DiffMedianBonusPercent",
        "MaleBonusPercent",
        "FemaleBonusPercent",
        "MaleLowerQuartile",
        "FemaleLowerQuartile",
        "MaleLowerMiddleQuartile",
        "FemaleLowerMiddleQuartile",
        "MaleUpperMiddleQuartile",
        "FemaleUpperMiddleQuartile",
        "MaleTopQuartile",
        "FemaleTopQuartile",
    ]
    date_fields = ["DueDate", "DateSubmitted"]
    bool_fields = ["SubmittedAfterTheDeadline"]
    date_format = {
        "DueDate": "%Y/%m/%d %H:%M:%S",
        "DateSubmitted": "%Y/%m/%d %H:%M:%S",
    }
    source = {
        "title": "Gender Pay Gap",
        "description": "",
        "identifier": "gpg",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Gender pay gap service",
            "website": "https://gender-pay-gap.service.gov.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://gender-pay-gap.service.gov.uk/viewing/download",
                "title": "Download gender pay gap data",
            }
        ],
    }
    models_to_delete = [GenderPayGap]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = {
            "update_websites": UPDATE_WEBSITES,
        }

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        for link in response.html.absolute_links:
            if "/download-data/" not in link:
                continue

            # last four digits are the year
            year = int(link[-4:])

            # download the file
            csv_response = self.session.get(link)

            with io.StringIO(csv_response.text) as a:
                csvreader = csv.DictReader(a)
                for k, row in enumerate(csvreader):
                    self.parse_row(row, year)

    def parse_url(self, url):
        if not isinstance(url, str):
            return None

        parsed = urlparse(url)

        for exclude in EXCLUDE_ADDRESS:
            if exclude in parsed.netloc:
                return None

        return "{uri.scheme}://{uri.netloc}/".format(uri=parsed)

    def parse_row(self, row, year):
        row = self.clean_fields(row)

        for k in row.keys():
            if not row[k]:
                continue
            elif k == "SicCodes":
                row[k] = [v.strip() for v in row[k].split(",") if v.strip()]
            elif k == "EmployerSize":
                for c in GenderPayGap.EmployerSizeChoices:
                    if row[k] == c.value:
                        row[k] = c

        if row.get("CompanyNumber"):
            row["org_id"] = "GB-COH-{}".format(row["CompanyNumber"])
        else:
            row["org_id"] = None

        row["CompanyWebsite"] = self.parse_url(row["CompanyLinkToGPGInfo"])

        row["Year"] = year
        row["scrape"] = self.scrape
        self.add_record(GenderPayGap, row)
