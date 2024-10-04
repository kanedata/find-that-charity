import io

from django.utils.text import slugify
from openpyxl import load_workbook

from ftc.management.commands._base_scraper import BaseScraper
from ftc.models import OrganisationClassification, Vocabulary, VocabularyEntries

UKG = "ukg"


class Command(BaseScraper):
    name = "ukgrantmaking"
    allowed_domains = ["ukgrantmaking.org"]
    start_urls = [
        "https://www.ukgrantmaking.org/wp-content/uploads/2024/06/uk-grantmaking-all-grantmakers-2022-23.xlsx",
    ]
    source = {
        "title": "UK Grantmaking Segments",
        "description": "",
        "identifier": "ukcat",
        "license": "http://creativecommons.org/licenses/by/4.0/",
        "license_name": "Creative Commons Attribution 4.0 International License",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "360Giving",
            "website": "https://www.threesixtygiving.org/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.ukgrantmaking.org/report/2024/methodology-data/#Full%20data",
                "title": "UK Grantmaking - Methodology and data",
            }
        ],
    }
    vocab = {
        UKG: {
            "title": "UK Grantmaking Segment",
            "description": """Categories and segments from UK Grantmaking, the definitive annual publication on grant funding in the UK.

It is a unique cross-sector collaboration between 360Giving, the Association of Charitable Foundations, the Association of Charitable Organisations, UK Community Foundations and London Funders. 

Find out more at [ukgrantmaking.org](https://www.ukgrantmaking.org/).
""",
        },
    }
    models_to_delete = [OrganisationClassification]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intialise_vocabulary()

    def intialise_vocabulary(self):
        self.logger.info("Fetching ICNPTSO")
        vocab, _ = Vocabulary.objects.update_or_create(
            slug=UKG,
            defaults=dict(
                description=self.vocab[UKG]["description"],
                title=self.vocab[UKG]["title"],
                single=False,
            ),
        )
        self.vocab_obj = vocab
        VocabularyEntries.objects.filter(vocabulary=vocab).update(current=False)
        self.vocab_cache = {}

    def parse_file(self, response, source_url):
        wb = load_workbook(io.BytesIO(response.content), read_only=True)
        latest_sheet = wb.active
        headers = []
        for k, row in enumerate(latest_sheet.rows):
            if not row[0].value:
                continue

            if not headers:
                headers = [c.value.lower() for c in row]
            else:
                record = dict(zip(headers, [c.value for c in row]))
                self.parse_row(record)

    def parse_row(self, record):
        segment = record.get("segment")
        category = record.get("category")

        if (category, segment) in self.vocab_cache:
            vocabulary_id = self.vocab_cache[(category, segment)]
        else:
            category_obj, _ = VocabularyEntries.objects.update_or_create(
                vocabulary=self.vocab_obj,
                code=slugify(category),
                parent=None,
                defaults=dict(
                    title=category,
                    current=True,
                ),
            )
            segment_obj, _ = VocabularyEntries.objects.update_or_create(
                vocabulary=self.vocab_obj,
                code=slugify(category) + "-" + slugify(segment),
                parent=category_obj,
                defaults=dict(
                    title=segment,
                    current=True,
                ),
            )
            vocabulary_id = segment_obj.id
            self.vocab_cache[(category, segment)] = vocabulary_id

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
