import csv
import datetime
import io
import zipfile

import tqdm
from django.utils.text import slugify

from charity.management.commands._oscr_sql import UPDATE_OSCR
from charity.models import CharityRaw
from ftc.management.commands._base_scraper import CSVScraper
from ftc.models import (
    Organisation,
    OrganisationClassification,
    OrganisationLink,
    OrganisationLocation,
    Vocabulary,
)
from ftc.models.vocabulary import VocabularyEntries


class Command(CSVScraper):
    name = "oscr"
    allowed_domains = ["oscr.org.uk", "githubusercontent.com"]
    start_urls = [
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityRegDownload",
        "https://www.oscr.org.uk/umbraco/Surface/FormsSurface/CharityFormerRegDownload",
    ]
    org_id_prefix = "GB-SC"
    id_field = "Charity Number"
    date_fields = ["Registered Date", "Year End", "Ceased Date"]
    date_format = {
        "Registered Date": "%d/%m/%Y %H:%M",
        "Ceased Date": "%d/%m/%Y %H:%M",
        "Year End": "%d/%m/%Y",
    }
    source = {
        "title": "Office of Scottish Charity Regulator Charity Register Download",
        "description": "",
        "identifier": "oscr",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
        "license_name": "Open Government Licence v2.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Office of Scottish Charity Regulator",
            "website": "https://www.oscr.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "",
                "title": "Office of Scottish Charity Regulator Charity Register Download",
            }
        ],
    }
    orgtypes = [
        "Registered Charity",
        "Registered Charity (Scotland)",
    ]
    models_to_delete = [
        Organisation,
        OrganisationLink,
        OrganisationLocation,
        OrganisationClassification,
    ]
    charity_sql = UPDATE_OSCR
    vocab_fields = ["Beneficiaries", "Activities", "Purposes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_records = []
        self.vocabularies = {}
        self.seen_org_ids = set()
        for f in self.vocab_fields:
            v, _ = Vocabulary.objects.get_or_create(
                slug="{}_{}".format(self.name, f.lower()),
                defaults=dict(
                    single=False,
                    title=f"{f} ({self.name.upper()})",
                    description=f"{f} as chosen by the organisation in their annual return to {self.source['publisher']['name']}. Organisations can chose multiple categories.",
                ),
            )
            self.vocabularies[f] = {
                "vocabulary": v,
                "entries": {entry.title: entry.id for entry in v.entries.all()},
            }

    def add_vocabulary_entry(self, vocab, entry_title):
        existing_id = (
            self.vocabularies.get(vocab, {}).get("entries", {}).get(entry_title)
        )
        if existing_id:
            return existing_id
        new_vocab, _ = VocabularyEntries.objects.get_or_create(
            vocabulary=self.vocabularies[vocab]["vocabulary"],
            code=slugify(entry_title),
            defaults=dict(
                title=entry_title,
                current=True,
            ),
        )
        self.vocabularies[vocab]["entries"][entry_title] = new_vocab.id
        return new_vocab.id

    def parse_file(self, response, source_url):
        try:
            z = zipfile.ZipFile(io.BytesIO(response.content))
        except zipfile.BadZipFile:
            self.logger.info(response.content[0:1000])
            raise
        for f in z.infolist():
            self.logger.info("Opening: {}".format(f.filename))
            with z.open(f) as csvfile:
                reader = csv.DictReader(io.TextIOWrapper(csvfile, encoding="utf8"))
                rowcount = 0
                for row in reader:
                    rowcount += 1

                    self.parse_row(row)
        z.close()

    def parse_row(self, record):

        record = self.clean_fields(record)

        address, _ = self.split_address(
            record.get("Principal Office/Trustees Address", ""), get_postcode=False
        )

        org_types = [
            self.orgtype_cache["registered-charity"],
            self.orgtype_cache["registered-charity-scotland"],
        ]
        if record.get("Regulatory Type") == "Cross Border":
            org_types.append(self.add_org_type("Cross Border Charity"))
        elif record.get("Regulatory Type") != "Standard" and record.get(
            "Regulatory Type"
        ):
            org_types.append(self.add_org_type(record.get("Regulatory Type")))
        if record.get("Designated religious body") == "Yes":
            org_types.append(self.add_org_type("Designated religious body"))

        if (
            record.get("Constitutional Form")
            == "SCIO (Scottish Charitable Incorporated Organisation)"
        ):
            org_types.append(
                self.add_org_type("Scottish Charitable Incorporated Organisation")
            )
        elif (
            record.get("Constitutional Form")
            == "CIO (Charitable Incorporated Organisation, E&W)"
        ):
            org_types.append(self.add_org_type("Charitable Incorporated Organisation"))
        elif (
            record.get("Constitutional Form")
            == "Company (the charity is registered with Companies House)"
        ):
            org_types.append(self.add_org_type("Registered Company"))
            org_types.append(self.add_org_type("Incorporated Charity"))
        elif (
            record.get("Constitutional Form")
            == "Trust (founding document is a deed of trust) (other than educational endowment)"
        ):
            org_types.append(self.add_org_type("Trust"))
        elif record.get("Constitutional Form") != "Other" and record.get(
            "Constitutional Form"
        ):
            org_types.append(self.add_org_type(record.get("Constitutional Form")))

        org_ids = [self.get_org_id(record)]

        if org_ids[0] in self.seen_org_ids:
            self.logger.debug("Skipping duplicate org: {}".format(org_ids[0]))
            return

        self.raw_records.append(record)

        for v in self.vocabularies:
            if not record.get(v):
                continue
            reader = csv.reader([record.get(v, "")], delimiter=",", quotechar="'")
            for value in next(reader):
                entry = self.add_vocabulary_entry(v, value)
                self.add_record(
                    OrganisationClassification,
                    {
                        "org_id": self.get_org_id(record),
                        "vocabulary_id": entry,
                        "scrape": self.scrape,
                        "source": self.source,
                        "spider": self.name,
                    },
                )

        self.add_org_record(
            Organisation(
                **{
                    "org_id": self.get_org_id(record),
                    "name": record.get("Charity Name"),
                    "charityNumber": record.get(self.id_field),
                    "companyNumber": None,
                    "streetAddress": address[0],
                    "addressLocality": address[1],
                    "addressRegion": address[2],
                    "addressCountry": "Scotland",
                    "postalCode": self.parse_postcode(record.get("Postcode")),
                    "telephone": None,
                    "alternateName": [record.get("Known As")]
                    if record.get("Known As")
                    else [],
                    "email": None,
                    "description": record.get("Objectives"),
                    "organisationType": [o.slug for o in org_types],
                    "organisationTypePrimary": org_types[0],
                    "url": self.parse_url(record.get("Website")),
                    "latestIncome": int(record["Most recent year income"])
                    if record.get("Most recent year income")
                    else None,
                    "dateModified": datetime.datetime.now(),
                    "dateRegistered": record.get("Registered Date"),
                    "dateRemoved": record.get("Ceased Date"),
                    "active": record.get("Charity Status") != "Removed",
                    "parent": record.get(
                        "Parent Charity Name"
                    ),  # @TODO: More sophisticated getting of parent charities here
                    "orgIDs": org_ids,
                    "scrape": self.scrape,
                    "source": self.source,
                    "spider": self.name,
                    "org_id_scheme": self.orgid_scheme,
                }
            )
        )

        self.seen_org_ids.add(self.get_org_id(record))

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting charity records
        self.logger.info("Inserting CharityRaw records")
        CharityRaw.objects.bulk_create(self.get_bulk_create())
        self.logger.info("CharityRaw records inserted")

        self.logger.info("Deleting old CharityRaw records")
        CharityRaw.objects.filter(spider__exact=self.name,).exclude(
            scrape_id=self.scrape.id,
        ).delete()
        self.logger.info("Old CharityRaw records deleted")

        # execute SQL statements
        self.execute_sql_statements(self.charity_sql)

    def get_bulk_create(self):

        for record in tqdm.tqdm(self.raw_records):
            yield CharityRaw(
                org_id=self.get_org_id(record),
                data=record,
                scrape=self.scrape,
                spider=self.name,
            )
