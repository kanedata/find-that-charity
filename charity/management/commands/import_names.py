from charity.models import CharityName
from ftc.management.commands._base_scraper import CSVScraper


class Command(CSVScraper):
    name = "charity_names"
    allowed_domains = ["gist.githubusercontent.com"]
    start_urls = [
        "https://raw.githubusercontent.com/drkane/charity-lookups/master/charity-names.csv",
    ]
    source = {
        "title": "Charity Alternative Names",
        "description": "",
        "identifier": "charity_names",
        "license": "http://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International License",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Find that Charity",
            "website": "https://github.com/drkane/charity-lookups",
        },
        "distribution": [
            {
                "downloadURL": "https://raw.githubusercontent.com/drkane/charity-lookups/master/charity-names.csv",
                "accessURL": "https://github.com/drkane/charity-lookups/blob/master/charity-names.csv",
                "title": "Find that Charity alternative names",
            }
        ],
    }
    upsert_models = {CharityName: {"by": ["charity_id", "name"]}}

    def parse_row(self, row):
        record = self.clean_fields(row)
        if row["alternative_name"]:
            self.add_record(
                CharityName,
                {
                    "charity_id": record["org_id"],
                    "name": record["alternative_name"],
                    "normalisedName": record["alternative_name"],
                    "name_type": "Alternative Name",
                },
            )
