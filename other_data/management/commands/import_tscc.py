import csv
import io
import zipfile

from ftc.management.commands._base_scraper import CSVScraper
from other_data.models import CIC


class Command(CSVScraper):
    name = "tscc"
    allowed_domains = ["uk-third-sector-database.github.io"]
    start_urls = [
        "https://github.com/uk-third-sector-database/tso-database-builder/raw/refs/heads/main/tcss-cic36-forms-Feb2026.zip?download=",
    ]
    int_fields = [
        "regy",
        "remy",
    ]
    source = {
        "title": "CIC 36 Forms",
        "description": "Beneficiaries, activities and use of surplus from incorporation documents of Community Interest Companies. One row per company, up to ten activities per record.",
        "identifier": "tscc-cic-36-forms",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "The UK Third and Civil Society Sector Database",
            "website": "https://www.uk-third-sector-database.org/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://uk-third-sector-database.github.io/data/",
                "title": "Mapping and analysing the third and civil society sectors",
            }
        ],
    }
    models = [CIC]
    upsert_models = {CIC: {"by": ["uid"]}}

    def parse_file(self, response, source_url):
        try:
            z = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile:
            self.logger.info(response.content[0:1000])
            raise
        for f in z.infolist():
            self.logger.info("Opening: {}".format(f.filename))
            with z.open(f) as csvfile:
                if not f.filename.endswith(".csv"):
                    continue
                csvreader = csv.DictReader(io.TextIOWrapper(csvfile, encoding="utf8"))
                for k, row in enumerate(csvreader):
                    self.parse_row(row)

    def parse_row(self, row):
        row = self.clean_fields(row)
        row["spider"] = self.name
        row["scrape_id"] = self.scrape.id
        row["source_id"] = self.source.id
        self.add_record(CIC, row)
