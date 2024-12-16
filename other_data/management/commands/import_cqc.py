import io

from openpyxl.utils.datetime import from_excel
from pyexcel_ods3 import get_data
from tqdm import tqdm

from ftc.management.commands._base_scraper import HTMLScraper
from other_data.models import CQCBrand, CQCLocation, CQCProvider

UPDATE_GEODATA = """
    insert into ftc_organisationlocation (
        org_id,
        name,
        "geoCode",
        "geoCodeType",
        "locationType",
        geo_iso,
        "spider",
        "source_id",
        "scrape_id"
    )
    select cqc_p.org_id as "org_id",
        cqc_l.address_postcode as "name",
        cqc_l.address_postcode as "geoCode",
        'PC' as "geoCodeType",
        'SITE' as "locationType",
        'GB' as "geo_iso",
        cqc_l.spider as "spider",
        cqc_l.spider as "source_id",
        cqc_l.scrape_id as "scrape_id"
    from other_data_cqclocation cqc_l
        inner join other_data_cqcprovider cqc_p
            on cqc_l.provider_id = cqc_p.id
                and cqc_l.scrape_id = cqc_p.scrape_id
        inner join ftc_organisation fo
            on cqc_p.org_id = fo.org_id
    where cqc_l.status = 'Active'
    on conflict (org_id, "name", "geoCodeType", "locationType", spider, source_id, scrape_id) do nothing;
"""


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
    bool_fields = ["Care home?", "Inherited Rating (Y/N)"]
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
    models_to_delete = [CQCBrand, CQCProvider, CQCLocation]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_sql = {
            "add CQC locations": UPDATE_GEODATA,
        }

        self.field_lookup = {}
        self.brand_ids = set()
        self.provider_ids = set()
        for m in self.models:
            for k in m._meta.fields:
                self.field_lookup[k.verbose_name] = {
                    "model": m.__name__,
                    "field": k.name,
                }

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        for link in response.html.absolute_links:
            if not link.endswith(".ods"):
                continue

            if "HSCA_Active_Locations".lower() in link.lower():
                # parse active locations
                # https://www.cqc.org.uk/sites/default/files/April_2021_HSCA_Active_Locations.ods
                self.parse_ods(link)
            elif "Deactivated_Locations".lower() in link.lower():
                # parse inactive locations
                # https://www.cqc.org.uk/sites/default/files/Deactivated_locations_01_April_2021.ods
                self.parse_ods(link)

    def parse_ods(self, link):
        self.logger.info("Downloading: {}".format(link))
        r = self.session.get(link)
        r.raise_for_status()

        wb = get_data(io.BytesIO(r.content))
        for ws_name in wb:
            if ws_name == "README":
                continue
            if ws_name == "Dual_Registration_Locations":
                continue
            self.logger.info("Loading from sheet '{}'".format(ws_name))
            ws = wb[ws_name]
            headers = None

            for row in tqdm(ws):
                if not headers:
                    headers = row
                    continue
                self.parse_row(dict(zip(headers, row)))

    def clean_fields(self, row):
        record = super().clean_fields(row)

        for f in self.date_fields:
            if record.get(f) and isinstance(record.get(f), int):
                record[f] = from_excel(record[f])

        return record

    def parse_row(self, row):
        row = self.clean_fields(row)

        this_model = {m.__name__: {} for m in self.models}

        for k in row:
            if k in self.field_lookup:
                meta = self.field_lookup[k]
                this_model[meta["model"]][meta["field"]] = row[k]

        # if row is blank then ignore
        if not this_model["CQCProvider"].get("id"):
            return

        # add IDs
        this_model["CQCLocation"]["provider_id"] = this_model["CQCProvider"]["id"]
        if not this_model["CQCBrand"].get("id"):
            this_model["CQCBrand"]["id"] = None
        elif this_model["CQCBrand"]["id"] == "-":
            this_model["CQCBrand"]["id"] = None
        if this_model["CQCBrand"].get("name", "").startswith("BRAND "):
            this_model["CQCBrand"]["name"] = this_model["CQCBrand"]["name"][6:]
        this_model["CQCProvider"]["brand_id"] = this_model["CQCBrand"]["id"]

        if this_model["CQCProvider"]["charity_number"]:
            charity_number = str(this_model["CQCProvider"]["charity_number"])
            if charity_number.upper().startswith("SC"):
                this_model["CQCProvider"]["org_id"] = "GB-SC-{}".format(
                    charity_number.upper()
                )
            else:
                this_model["CQCProvider"]["org_id"] = "GB-CHC-{}".format(charity_number)
        elif this_model["CQCProvider"]["company_number"]:
            this_model["CQCProvider"]["org_id"] = "GB-COH-{}".format(
                this_model["CQCProvider"]["company_number"]
            )

        # add scrape id
        this_model["CQCLocation"]["scrape_id"] = self.scrape.id
        this_model["CQCProvider"]["scrape_id"] = self.scrape.id
        this_model["CQCBrand"]["scrape_id"] = self.scrape.id

        for m in self.models:
            if this_model[m.__name__]["id"]:
                if (
                    m.__name__ == "CQCProvider"
                    and this_model[m.__name__]["id"] in self.provider_ids
                ):
                    return
                if (
                    m.__name__ == "CQCBrand"
                    and this_model[m.__name__]["id"] in self.brand_ids
                ):
                    return
                self.add_record(m, this_model[m.__name__])
                if m.__name__ == "CQCProvider":
                    self.provider_ids.add(this_model[m.__name__]["id"])
                if m.__name__ == "CQCBrand":
                    self.brand_ids.add(this_model[m.__name__]["id"])
