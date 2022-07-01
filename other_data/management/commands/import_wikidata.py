from ftc.management.commands._base_scraper import HTMLScraper
from other_data.models import WikiDataItem

SPARQL_QUERY = """
SELECT ?item ?itemLabel ?charity ?article ?articlename ?twitter ?facebook ?grid WHERE {
  ?item wdt:P3057 ?charity.
  OPTIONAL {?article schema:about ?item ;
              schema:name ?articlename .
  ?article schema:isPartOf <https://en.wikipedia.org/>.}
  OPTIONAL { ?item wdt:P2002 ?twitter. }
  OPTIONAL { ?item wdt:P2013 ?facebook. }
  OPTIONAL { ?item wdt:P2427 ?grid. }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}  ORDER BY ?itemLabel
"""


class Command(HTMLScraper):
    name = "wd"
    allowed_domains = ["query.wikidata.org"]
    start_urls = [
        "https://query.wikidata.org/sparql",
    ]
    float_fields = []
    date_fields = []
    bool_fields = []
    date_format = {}
    source = {
        "title": "Wikidata",
        "description": "",
        "identifier": "gpg",
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "license_name": " CC0 1.0 Universal (CC0 1.0) Public Domain Dedication ",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Wikidata",
            "website": "https://www.wikidata.org/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://query.wikidata.org/",
                "title": "Wikidata Query Service",
            }
        ],
    }
    models_to_delete = [WikiDataItem]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = {}

    def fetch_file(self):
        self.files = {}
        for u in self.start_urls:
            r = self.session.get(u, params={"format": "json", "query": SPARQL_QUERY})
            r.raise_for_status()
            self.set_access_url(u)
            self.files[u] = r.json()

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        for row in response["results"]["bindings"]:
            self.parse_row(row, source_url)

    def clean_fields(self, record):
        new_record = {}
        for k, v in record.items():
            new_record[k] = v.get("value")
        return super().clean_fields(new_record)

    def parse_row(self, row, year):
        row = self.clean_fields(row)
        if not row.get("charity") or not row.get("item"):
            return
        result = {
            "org_id": "GB-CHC-{}".format(row.get("charity")),
            "wikidata_id": row.get("item"),
            "wikipedia_url": row.get("article"),
            "twitter": row.get("twitter"),
            "facebook": row.get("facebook"),
            "grid_id": "XI-GRID-{}".format(row.get("grid"))
            if row.get("grid")
            else None,
            "spider": "wd",
            "scrape": self.scrape,
        }
        self.add_record(WikiDataItem, result)
