import csv
import datetime
import io
import logging
import re
from collections import defaultdict

import requests
import requests_cache
import validators
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, transaction
from django.utils.text import slugify

from ftc.management.commands._bulk_upsert import bulk_upsert
from ftc.management.commands._db_logger import ScrapeHandler
from ftc.models import (
    Organisation,
    OrganisationLink,
    OrganisationLocation,
    OrganisationType,
    OrgidScheme,
    Scrape,
    Source,
)

DEFAULT_DATE_FORMAT = "%Y-%m-%d"


class BaseScraper(BaseCommand):
    date_format = DEFAULT_DATE_FORMAT
    date_fields = []
    bool_fields = []
    float_fields = []
    encoding = "utf8"
    orgtypes = []
    bulk_limit = 10000
    models_to_delete = [
        Organisation,
        OrganisationLink,
        OrganisationLocation,
    ]
    model_updates = {}
    upsert_models = {}
    expected_records = 1
    verify_certificate = True
    user_agent = settings.DEFAULT_USER_AGENT

    postcode_regex = re.compile(
        r"([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z][A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|([A-Za-z][A-Ha-hJ-Yj-y][0-9][A-Za-z]?))))\s?[0-9][A-Za-z]{2})"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scrape = Scrape(
            status=Scrape.ScrapeStatus.RUNNING,
            spider=self.name,
            log="",
        )
        self.scrape.save()
        self.object_count = defaultdict(lambda: 0)
        self.error_count = 0
        self.orgtype_cache = {}
        self.records = defaultdict(list)
        self.location_records = defaultdict(list)

        # set up logging
        self.logger = logging.getLogger("ftc.{}".format(self.name))
        self.scrape_logger = ScrapeHandler(self.scrape, self.expected_records)
        scrape_log_format = logging.Formatter(
            "{levelname} {asctime} [{name}] {message}", style="{"
        )
        self.scrape_logger.setFormatter(scrape_log_format)
        self.scrape_logger.setLevel(logging.INFO)
        self.logger.addHandler(self.scrape_logger)

        self.post_sql = {}
        self.cursor = connections["data"].cursor()

    def add_arguments(self, parser):
        parser.add_argument(
            "--cache",
            action="store_true",
            help="Cache request",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Run in debug mode",
        )

    def set_session(self, install_cache=False):
        if install_cache:
            self.logger.info("Using requests_cache")
            requests_cache.install_cache("http_cache")
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def handle(self, *args, **options):
        self.debug = options.get("debug")
        try:
            with transaction.atomic("data"):
                self.run_scraper(*args, **options)
        except Exception as err:
            self.logger.exception(err)
            self.scrape_logger.teardown()
            raise
        self.cursor.close()

    def run_scraper(self, *args, **options):
        # set up cache if we're caching
        self.set_session(options.get("cache"))

        # set up orgidscheme object
        if hasattr(self, "org_id_prefix"):
            self.orgid_scheme, _ = OrgidScheme.objects.get_or_create(
                code=self.org_id_prefix,
                defaults={"data": {}},
            )

        # save any orgtypes
        if self.orgtypes:
            self.logger.info("Saving orgtypes")
            for o in self.orgtypes:
                self.add_org_type(o)
            self.logger.info("orgtypes saved")

        # save any sources
        self.logger.info("saving sources")
        self.save_sources()
        self.logger.info("sources saved")

        # fetch needed files
        self.logger.info("fetching files")
        self.fetch_file()
        self.logger.info("{:,.0f} files fetched".format(len(self.files)))

        # process needed files
        self.logger.info("Processing files")
        for u, f in self.files.items():
            self.parse_file(f, u)
        self.logger.info("Files processed.")
        for model, count in self.object_count.items():
            self.logger.info("Found {:,.0f} {} records".format(count, model.__name__))

        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")

    def close_spider(self):
        results = {}
        self.get_link_records()
        for model, records in self.records.items():
            self.save_records(model)
            if model == OrganisationLink:
                results["link_records"] = len(records)
            results[f"{model.__name__}_records"] = len(records)
        results["records"] = sum(self.object_count.values())
        self.scrape.items = sum(self.object_count.values())

        # if we've been successfull then delete previous items
        self.logger.info("Deleting previous records")
        for model in self.models_to_delete:
            self.logger.info(
                "Deleting previous {} records".format(
                    model.__name__,
                )
            )
            delete_sql = """
                DELETE
                FROM "{db_table}"
                WHERE (
                    "{db_table}"."spider" = %s
                    AND NOT ("{db_table}"."scrape_id" = %s)
                );
            """.format(db_table=model._meta.db_table)
            self.cursor.execute(
                delete_sql,
                [
                    self.name,
                    self.scrape.id,
                ],
            )
            self.logger.info(
                "Deleted {:,.0f} previous {} records".format(
                    self.cursor.rowcount,
                    model.__name__,
                )
            )

        # do any SQL actions after the data has been included
        self.execute_sql_statements(self.post_sql)

        self.scrape.errors = self.error_count
        self.scrape.result = results
        self.scrape_logger.teardown()

    def execute_sql_statements(self, sqls):
        for sql_name, sql in sqls.items():
            self.logger.info("Starting SQL: {}".format(sql_name))
            self.cursor.execute(
                sql,
                {
                    "spider_name": self.name,
                    "scrape_id": self.scrape.id,
                    "source_id": self.source.id
                    if getattr(self, "source", None)
                    else None,
                },
            )
            self.logger.info("Finished SQL: {}".format(sql_name))

    def add_org_record(self, record):
        self.add_record(Organisation, record)

    def add_record(self, model, record):
        if isinstance(record, dict) and (model not in self.upsert_models):
            record = model(**record)
        self.records[model].append(record)
        if len(self.records[model]) >= self.bulk_limit:
            self.save_records(model)

    def save_records(self, model):
        self.logger.info(
            "Saving {:,.0f} {} records".format(len(self.records[model]), model.__name__)
        )
        if model in self.upsert_models:
            bulk_upsert(
                model,
                self.upsert_models[model].get(
                    "fields",
                    [
                        f.get_attname_column()[1]
                        for f in model._meta.get_fields()
                        if f.name != "id"
                    ],
                ),
                self.records[model],
                self.upsert_models[model]["by"],
            )
        else:
            model.objects.bulk_create(
                self.records[model], **self.model_updates.get(model, {})
            )
        self.object_count[model] += len(self.records[model])
        self.logger.info(
            "Saved {:,.0f} {} records ({:,.0f} total)".format(
                len(self.records[model]),
                model.__name__,
                self.object_count[model],
            )
        )
        self.get_link_records()
        self.records[model] = []

    def add_location_record(self, record):
        self.add_record(OrganisationLocation, record)

    def save_sources(self):
        if hasattr(self, "source"):
            sources = [self.source]
        else:
            # No sources found
            return

        for s in sources:
            # fix datetimes
            for f in ["issued", "modified"]:
                if not s.get(f):
                    s[f] = datetime.datetime.now().strftime("%Y-%m-%d")
            self.source, _ = Source.objects.update_or_create(
                id=s["identifier"], defaults={"data": s}
            )

    def set_access_url(self, url, overwrite=False):
        if not self.source.data["distribution"][0]["accessURL"] or overwrite:
            self.source.data["distribution"][0]["accessURL"] = url
            self.source.save()

    def set_download_url(self, url, overwrite=False):
        if not self.source.data["distribution"][0]["downloadURL"] or overwrite:
            self.source.data["distribution"][0]["downloadURL"] = url
            self.source.save()

    def fetch_file(self):
        self.files = {}
        if hasattr(self, "start_urls"):
            for u in self.start_urls:
                self.set_download_url(u)
                r = self.session.get(u, verify=self.verify_certificate)
                r.raise_for_status()
                self.files[u] = r

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        pass

    def parse_row(self, row):
        return self.clean_fields(row)

    def get_link_records(self):
        links = set()

        # save existing link records
        for record in self.records[OrganisationLink]:
            links.add(tuple(sorted((record.org_id_a, record.org_id_b))))
        self.records[OrganisationLink] = []

        # fetch any links that need to be created
        for o in self.records[Organisation]:
            for orgid in o.orgIDs:
                if orgid == o.org_id:
                    continue
                links.add(tuple(sorted((orgid, o.org_id))))

        # create new link records
        for link in links:
            self.records[OrganisationLink].append(
                OrganisationLink(
                    org_id_a=link[0],
                    org_id_b=link[1],
                    spider=self.name,
                    scrape=self.scrape,
                    source=self.source,
                )
            )

    def get_org_id(self, record):
        return "-".join([self.org_id_prefix, str(record.get(self.id_field))])

    def clean_fields(self, record, blank_values=[""]):
        record = {k.strip(): v for k, v in record.items()}

        for f in record.keys():
            # clean blank values
            if record[f] in blank_values:
                record[f] = None

            # clean date fields
            elif f in self.date_fields and isinstance(record[f], str):
                date_format = self.date_format
                if isinstance(date_format, dict):
                    date_format = date_format.get(f, DEFAULT_DATE_FORMAT)

                try:
                    if record.get(f):
                        record[f] = datetime.datetime.strptime(
                            record.get(f).strip(), date_format
                        )
                except ValueError:
                    self.logger.warn(
                        "Could not convert date field {} with value '{}' (expected format '{}')".format(
                            f,
                            record[f],
                            date_format,
                        )
                    )
                    record[f] = None

            # clean boolean fields
            elif f in self.bool_fields:
                if isinstance(record[f], str):
                    val = record[f].lower().strip()
                    if val in ["f", "false", "no", "0", "n"]:
                        record[f] = False
                    elif val in ["t", "true", "yes", "1", "y"]:
                        record[f] = True

            # clean float fields
            elif f in self.float_fields:
                if isinstance(record[f], str):
                    val = record[f].lower().strip()
                else:
                    val = record[f]
                try:
                    record[f] = float(val)
                except (ValueError, TypeError):
                    record[f] = None

            # strip string fields
            elif isinstance(record[f], str):
                record[f] = record[f].strip().replace("\x00", "")
        return record

    def slugify(self, value):
        value = value.lower()
        # replace values in brackets
        value = re.sub(r"\([0-9]+\)", "_", value).strip("_")
        # replace any non-alphanumeric characters
        value = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
        return value

    def parse_company_number(self, coyno):
        if not coyno:
            return None

        coyno = coyno.lstrip("0")

        coyno = coyno.strip()
        if coyno == "":
            return None

        # dummy company number sometimes used
        if coyno.rjust(8, "0") in ("01234567", "12345678"):
            return None

        if coyno.isdigit():
            return coyno.rjust(8, "0")

        return coyno

    def split_address(
        self, address_str, address_parts=3, separator=", ", get_postcode=True
    ):
        """
        Split an address string into postcode and address parts
        Will produce an array of exactly `address_parts` length, with None
        used in values that aren't present
        """
        if address_str is None:
            return ([None for n in range(address_parts)], None)

        address = [a.strip() for a in address_str.split(separator.strip())]
        postcode = None

        # if our list is greater than one item long then
        # we assume the last item is a postcode
        if get_postcode:
            if len(address) > 1:
                potential_postcode = self.parse_postcode(address[-1])
                if potential_postcode and self.postcode_regex.match(potential_postcode):
                    postcode = potential_postcode
                    address = address[0:-1]

        # make a new address list that's exactly the right length
        new_address = [None for n in range(address_parts)]
        for k, _ in enumerate(new_address):
            if len(address) > k:
                if k + 1 == address_parts:
                    new_address[k] = separator.join(address[k:])
                else:
                    new_address[k] = address[k]

        return new_address, postcode

    def parse_url(self, url):
        if url is None:
            return None

        url = url.strip()

        if validators.url(url):
            return url

        if validators.url("http://%s" % url):
            return "http://%s" % url

        if url in [
            "n.a",
            "non.e",
            ".0",
            "-.-",
            ".none",
            ".nil",
            "N/A",
            "TBC",
            "under construction",
            ".n/a",
            "0.0",
            ".P",
            b"",
            "no.website",
        ]:
            return None

        for i in [
            "http;//",
            "http//",
            "http.//",
            "http:\\\\",
            "http://http://",
            "www://",
            "www.http://",
        ]:
            url = url.replace(i, "http://")
        url = url.replace("http:/www", "http://www")

        for i in ["www,", ":www", "www:", "www/", "www\\\\", ".www"]:
            url = url.replace(i, "www.")

        url = url.replace(",", ".")
        url = url.replace("..", ".")

        if validators.url(url):
            return url

        if validators.url("http://%s" % url):
            return "http://%s" % url

    def parse_postcode(self, postcode):
        """
        standardises a postcode into the correct format
        """

        if postcode is None:
            return None

        # check for blank/empty
        # put in all caps
        postcode = postcode.strip().upper()
        if postcode == "":
            return None

        # replace any non alphanumeric characters
        postcode = re.sub("[^0-9a-zA-Z]+", "", postcode)

        if postcode == "":
            return None

        # check for nonstandard codes
        if len(postcode) > 7:
            return postcode

        first_part = postcode[:-3].strip()
        last_part = postcode[-3:].strip()

        # check for incorrect characters
        first_part = list(first_part)
        last_part = list(last_part)
        if last_part and last_part[0] == "O":
            last_part[0] = "0"

        return "%s %s" % ("".join(first_part), "".join(last_part))

    def add_org_type(self, orgtype):
        ot, _ = OrganisationType.objects.get_or_create(
            slug=slugify(orgtype),
            defaults=dict(title=orgtype),
        )
        self.orgtype_cache[ot.slug] = ot
        return ot


class CSVScraper(BaseScraper):
    def parse_file(self, response, source_url):
        try:
            csv_text = response.text
        except AttributeError:
            csv_text = response.content.decode(self.encoding)

        with io.StringIO(csv_text) as a:
            csvreader = csv.DictReader(a)
            for k, row in enumerate(csvreader):
                self.parse_row(row)


class SQLRunner(BaseScraper):
    expected_records = 0
    pass


class HTMLScraper(BaseScraper):
    def set_session(self, install_cache=False):
        if install_cache:
            self.logger.info("Using requests_cache")
            requests_cache.install_cache("http_cache")
        from requests_html import HTMLSession

        self.session = HTMLSession()
        self.session.headers.update({"User-Agent": self.user_agent})

    def fetch_file(self):
        self.files = {}
        for u in self.start_urls:
            r = self.session.get(u, verify=self.verify_certificate)
            r.raise_for_status()
            self.set_access_url(u)
            self.files[u] = r

    def parse_file(self, response, source_url):
        self.logger.info(source_url)
        pass
