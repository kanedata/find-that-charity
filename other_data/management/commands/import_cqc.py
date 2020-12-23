import io

from openpyxl import load_workbook
import tqdm

from ftc.management.commands._base_scraper import HTMLScraper
from other_data.models import CQCBrand, CQCLocation, CQCProvider


class Command(HTMLScraper):
    name = "cqc"
    allowed_domains = ["cqc.org.uk"]
    start_urls = [
        "https://www.cqc.org.uk/about-us/transparency/using-cqc-data",
    ]
    date_fields = [
        "Location HSCA start date",
        "Location HSCA End Date",
        "Publication Date",
        "Provider HSCA start date",
        "Provider HSCA End Date",
    ]
    float_fields = [
        "Location Latitude",
        "Location Longitude",
        "Provider Latitude",
        "Provider Longitude",
    ]
    bool_fields = ['Care home?', 'Inherited Rating (Y/N)']
    date_format = {
        "DueDate": "%d/%m/%Y %H:%M:%S",
        "DateSubmitted": "%d/%m/%Y %H:%M:%S",
    }
    source = {
        "title": "CQC Locations",
        "description": "",
        "identifier": "cqc",
        "license": "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "license_name": "Open Government Licence v3.0",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "Care Quality Commission",
            "website": "https://www.cqc.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://www.cqc.org.uk/about-us/transparency/using-cqc-data",
                "title": "Using CQC data",
            }
        ],
    }
    models = [CQCBrand, CQCProvider, CQCLocation]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cqc_records = {}
        self.field_lookup = {}
        for m in self.models:
            self.cqc_records[m.__name__] = {}
            for k in m._meta.fields:
                self.field_lookup[k.verbose_name] = {
                    'model': m.__name__,
                    'field': k.name,
                }

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        for link in response.html.absolute_links:
            if not link.endswith(".xlsx"):
                continue

            if "HSCA_Active_Locations" in link:
                # parse active locations
                # https://www.cqc.org.uk/sites/default/files/HSCA_Active_Locations_01_October_2020.xlsx
                self.parse_xlsx(link)
            elif "Deactivated_Locations" in link:
                # parse inactive locations
                # https://www.cqc.org.uk/sites/default/files/Deactivated_Locations1_October_2020.xlsx
                self.parse_xlsx(link)

    def parse_xlsx(self, link):
        self.logger.info("Downloading: {}".format(link))
        r = self.session.get(link)
        r.raise_for_status()

        wb = load_workbook(io.BytesIO(r.content), read_only=True)
        for ws in wb:
            if ws.title == "README":
                continue
            self.logger.info("Loading from sheet '{}'".format(ws.title))
            headers = None

            for row in ws.iter_rows(min_row=1, values_only=True):
                if not headers:
                    headers = row
                    continue
                row = self.clean_fields(dict(zip(headers, row)))
                this_model = {
                    m.__name__: {} for m in self.models
                }

                for k in row:
                    if k in self.field_lookup:
                        meta = self.field_lookup[k]
                        this_model[meta['model']][meta['field']] = row[k]

                # add IDs
                this_model['CQCLocation']['provider_id'] = this_model['CQCProvider']['id']
                if this_model['CQCBrand']['id'] == '-':
                    this_model['CQCBrand']['id'] = None
                this_model['CQCProvider']['brand_id'] = this_model['CQCBrand']['id']

                if this_model['CQCProvider']['charity_number']:
                    if this_model['CQCProvider']['charity_number'].upper().startswith("SC"):
                        this_model['CQCProvider']['org_id'] = "GB-SC-{}".format(
                            this_model['CQCProvider']['charity_number'].upper()
                        )
                    else:
                        this_model['CQCProvider']['org_id'] = "GB-CHC-{}".format(
                            this_model['CQCProvider']['charity_number']
                        )
                elif this_model['CQCProvider']['company_number']:
                    this_model['CQCProvider']['org_id'] = "GB-COH-{}".format(
                        this_model['CQCProvider']['company_number']
                    )

                # add scrape id
                this_model['CQCLocation']['scrape_id'] = self.scrape.id
                this_model['CQCProvider']['scrape_id'] = self.scrape.id
                this_model['CQCBrand']['scrape_id'] = self.scrape.id

                for m in self.models:
                    if this_model[m.__name__]['id']:
                        self.cqc_records[m.__name__][
                            this_model[m.__name__]['id']
                        ] = this_model[m.__name__]

    def bulk_create(self, m):
        for record in tqdm.tqdm(self.cqc_records[m.__name__].values()):
            yield m(**record)

    def close_spider(self):
        super(Command, self).close_spider()
        self.records = None
        self.link_records = None

        # now start inserting CQC records
        for m in self.models:
            self.logger.info("Inserting {} records".format(m.__name__))
            m.objects.all().delete()
            m.objects.bulk_create(self.bulk_create(m))
            self.logger.info("{} records inserted".format(m.__name__))
