import io
import csv

import tqdm

from ftc.management.commands._base_scraper import HTMLScraper
from other_data.models import GenderPayGap


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
    bool_fields = ['SubmittedAfterTheDeadline']
    date_format = {
        "DueDate": "%d/%m/%Y %H:%M:%S",
        "DateSubmitted": "%d/%m/%Y %H:%M:%S",
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_records = []

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

    def parse_row(self, row, year):
        row = self.clean_fields(row)

        for k in row.keys():
            if not row[k]:
                continue
            if k in self.float_fields:
                try:
                    row[k] = float(row[k])
                except TypeError:
                    row[k] = None
            elif k == "SicCodes":
                row[k] = [v.strip() for v in row[k].split(",") if v.strip()]
            elif k == "EmployerSize":
                for c in GenderPayGap.EmployerSizeChoices:
                    if row[k] == c.value:
                        row[k] = c

        if row.get('CompanyNumber'):
            row['org_id'] = 'GB-COH-{}'.format(row['CompanyNumber'])
        else:
            row['org_id'] = None

        row['Year'] = year
        row["scrape"] = self.scrape
        self.raw_records.append(row)

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting charity records
        self.logger.info("Inserting GenderPayGap records")
        GenderPayGap.objects.bulk_create(self.get_bulk_create())
        self.logger.info("GenderPayGap records inserted")

        self.logger.info("Deleting old GenderPayGap records")
        GenderPayGap.objects.exclude(
            scrape_id=self.scrape.id,
        ).delete()
        self.logger.info("Old GenderPayGap records deleted")

    def get_bulk_create(self):
        for record in tqdm.tqdm(self.raw_records):
            yield GenderPayGap(**record)
