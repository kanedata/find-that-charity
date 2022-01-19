import csv
import io

import requests

from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import OrganisationClassification, Vocabulary, VocabularyEntries

UKCAT = "ukcat"
ICNPTSO = "icnptso"


class Command(CSVScraper):
    name = "ukcat"
    allowed_domains = ["gist.githubusercontent.com"]
    start_urls = [
        "https://raw.githubusercontent.com/charity-classification/ukcat/main/data/charities_active-ukcat.csv",
        "https://raw.githubusercontent.com/charity-classification/ukcat/main/data/charities_inactive-ukcat.csv",
        "https://raw.githubusercontent.com/charity-classification/ukcat/main/data/charities_active-icnptso.csv",
        "https://raw.githubusercontent.com/charity-classification/ukcat/main/data/charities_inactive-icnptso.csv",
    ]
    source = {
        "title": "UK Charity Activity Tags",
        "description": "",
        "identifier": "ukcat",
        "license": "http://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International License",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "UK Charity Classification",
            "website": "https://charityclassification.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://charityclassification.org.uk/data/outputs/",
                "title": "UK Charity Classification  - Results and Outputs",
            }
        ],
    }
    vocab = {
        UKCAT: {
            "title": "UK Charity Activity Tags",
            "code_url": "https://raw.githubusercontent.com/drkane/ukcat/main/data/ukcat.csv",
            "vocab": None,
            "entries": {},
            "field": "ukcat_code",
        },
        ICNPTSO: {
            "title": "International Classification of Non-profit and Third Sector Organizations (ICNP/TSO)",
            "code_url": "https://github.com/drkane/charity-lookups/raw/master/classification/icnptso.csv",
            "vocab": None,
            "entries": {},
            "field": "icnptso_code",
        },
    }
    models_to_delete = [OrganisationClassification]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fetch_icnptso()
        self.fetch_ukcat()

    def fetch_icnptso(self):
        self.logger.info("Fetching ICNPTSO")
        vocab, _ = Vocabulary.objects.update_or_create(
            title=self.vocab[ICNPTSO]["title"],
            defaults=dict(single=False),
        )
        self.vocab[ICNPTSO]["vocab"] = vocab
        VocabularyEntries.objects.filter(vocabulary=vocab).update(current=False)
        cache = {}
        for r in self.get_csv(self.vocab[ICNPTSO]["code_url"], encoding="utf-8-sig"):
            if not r.get("Sub-group") and not r.get("Group"):
                code = r.get("Section")
                parent = None
            elif not r.get("Sub-group"):
                code = r.get("Group")
                parent = cache.get(r.get("Section"))
            else:
                code = r.get("Sub-group")
                parent = cache.get(r.get("Group"))
            ve, _ = VocabularyEntries.objects.update_or_create(
                code=code,
                vocabulary=vocab,
                defaults={"title": r.get("Title"), "parent": parent, "current": True},
            )
            self.vocab[ICNPTSO]["entries"][ve.code] = ve

    def fetch_ukcat(self):
        self.logger.info("Fetching UK-CAT categories")
        vocab, _ = Vocabulary.objects.update_or_create(
            title=self.vocab[UKCAT]["title"],
            defaults={
                "single": False,
            },
        )
        self.vocab[UKCAT]["vocab"] = vocab
        VocabularyEntries.objects.filter(vocabulary=vocab).update(current=False)

        cache = {}
        for row in self.get_csv(self.vocab[UKCAT]["code_url"], encoding="utf-8-sig"):
            vocab_entry, _ = VocabularyEntries.objects.update_or_create(
                vocabulary=vocab,
                code=row["Code"],
                defaults={"title": row["tag"], "current": True},
            )
            cache[row["tag"]] = {
                "entry": vocab_entry,
                "row": row,
            }
            self.vocab[UKCAT]["entries"][vocab_entry.code] = vocab_entry

        for cat in cache.values():
            if (
                cat["row"]["Subcategory"]
                and cat["row"]["Subcategory"] != cat["row"]["tag"]
            ):
                cat["entry"].parent = cache[cat["row"]["Subcategory"]]["entry"]
                cat["entry"].save()
                continue
            if cat["row"]["Category"] and cat["row"]["Category"] != cat["row"]["tag"]:
                cat["entry"].parent = cache[cat["row"]["Category"]]["entry"]
                cat["entry"].save()
                continue

    def parse_row(self, record):
        for key, vocab in self.vocab.items():
            if record.get(vocab["field"]):
                vocabulary_id = vocab["entries"][record[vocab["field"]]].id
                break

        self.add_record(
            OrganisationClassification,
            {
                "org_id": record["org_id"],
                "vocabulary_id": vocabulary_id,
                "spider": self.name,
                "source": self.source,
                "scrape": self.scrape,
            },
        )

    def get_csv(self, url, encoding="utf8"):
        response = requests.get(url)
        csv_text = response.content.decode(encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(a)
            for k, row in enumerate(csvreader):
                yield row
