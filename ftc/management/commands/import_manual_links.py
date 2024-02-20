import csv
import datetime
import io

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import OrganisationLink, Source


# Look up manual links held in charity-lookups repository
class Command(CSVScraper):
    name = "manual_links"
    allowed_domains = ["raw.githubusercontent.com"]

    sources = [
        {
            "title": "Find that Charity Relationship Lookups",
            "description": "",
            "identifier": "ftc_lookups",
            "license": "",
            "license_name": "",
            "issued": "",
            "modified": "",
            "publisher": {
                "name": "Find that Charity",
                "website": "https://github.com/drkane/charity-lookups",
            },
            "distribution": [
                {
                    "downloadURL": "https://github.com/drkane/charity-lookups/raw/master/relationships/_sameas.csv",
                    "accessURL": "https://github.com/drkane/charity-lookups/tree/master/relationships",
                    "title": "Find that Charity Relationship Lookups",
                }
            ],
        }
    ]

    def fetch_file(self):
        self.files = {}
        self.source_cache = {}
        for s in self.sources:
            self.logger.info("Fetching: " + s["title"])
            self.source_cache[s["identifier"]], _ = Source.objects.update_or_create(
                id=s["identifier"],
                defaults={
                    "data": {
                        **{k: v for k, v in s.items() if not k.startswith("_")},
                        "modified": datetime.datetime.now().isoformat(),
                    }
                },
            )
            r = self.session.get(s["distribution"][0]["downloadURL"])
            r.raise_for_status()
            r.encoding = s.get("_encoding", "utf-8-sig")
            self.files[s["identifier"]] = r

    def get_link_records(self):
        pass

    def execute_sql_statements(self, statements):
        pass

    def parse_file(self, response, source):
        source = [s for s in self.sources if s["identifier"] == source][0]

        if source.get("_parse_csv"):
            return getattr(self, source.get("_parse_csv"))(response, source)

        record_count = 0
        with io.StringIO(response.text) as a:
            csvreader = csv.DictReader(a)
            for row in csvreader:
                if "_parse_row" in source:
                    row = source["_parse_row"](row)
                row["source"] = source["identifier"]
                if row.get("org_id_a") and row.get("org_id_b"):
                    self.add_record(
                        OrganisationLink,
                        OrganisationLink(
                            org_id_a=row["org_id_a"],
                            org_id_b=row["org_id_b"],
                            spider=self.name,
                            source=self.source_cache[source["identifier"]],
                            scrape=self.scrape,
                        ),
                    )
                    record_count += 1
        if record_count == 0:
            raise Exception("No records found")
        self.logger.info("{} records added [{}]".format(record_count, source["title"]))
