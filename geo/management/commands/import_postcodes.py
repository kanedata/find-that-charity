import csv
import datetime
import io
import zipfile

import tqdm

from ftc.management.commands._base_scraper import BaseScraper
from geo.models import Postcode


class Command(BaseScraper):

    name = "postcodes"
    bulk_limit = 50000

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            help="Source file for the NPSL data (should be a ZIP file)",
        )

    def run_scraper(self, *args, **options):

        # initialise records
        self.records = []
        self.object_count = 0

        # delete existing records
        Postcode.objects.all().delete()

        # download the file
        if options["source"].startswith("http"):
            self.set_session(False)
            self.logger.info("Downloading from {}".format(options["source"]))
            nspl = self.session.get(options["source"])
            nspl.raise_for_status()
            nspl_f = io.BytesIO(nspl.content)
        else:
            self.logger.info("Opening {}".format(options["source"]))
            nspl_f = open(options["source"], "rb")

        # go through each postcode file and create records
        with zipfile.ZipFile(nspl_f) as z:
            for f in z.infolist():
                if not f.filename.startswith(
                    "Data/multi_csv/"
                ) or not f.filename.endswith(".csv"):
                    continue
                with z.open(f) as csvfile:
                    reader = csv.DictReader(
                        io.TextIOWrapper(csvfile, encoding="latin1")
                    )
                    self.logger.info("Opening file {}".format(f.filename))
                    for row in tqdm.tqdm(reader):
                        self.parse_row(row)

        self.close_spider()

    def parse_row(self, row):

        for k, v in row.items():
            if not v or v == "":
                row[k] = None

        def parse_date(value):
            if not value or value == "":
                return None
            return datetime.date(
                int(value[0:4]),
                int(value[4:6]),
                1,
            )

        self.add_record(
            pcd=row.get("pcd"),
            pcd2=row.get("pcd2"),
            pcds=row.get("pcds"),
            dointr=parse_date(row.get("dointr")),
            doterm=parse_date(row.get("doterm")),
            usertype=row.get("usertype"),
            oseast1m=row.get("oseast1m"),
            osnrth1m=row.get("osnrth1m"),
            osgrdind=row.get("osgrdind"),
            oa11=row.get("oa11"),
            cty=row.get("cty"),
            ced=row.get("ced"),
            laua=row.get("laua"),
            ward=row.get("ward"),
            hlthau=row.get("hlthau"),
            nhser=row.get("nhser"),
            ctry=row.get("ctry"),
            rgn=row.get("rgn"),
            pcon=row.get("pcon"),
            eer=row.get("eer"),
            teclec=row.get("teclec"),
            ttwa=row.get("ttwa"),
            pct=row.get("pct"),
            nuts=row.get("nuts"),
            npark=row.get("park"),
            lsoa11=row.get("lsoa11"),
            msoa11=row.get("msoa11"),
            wz11=row.get("wz11"),
            ccg=row.get("ccg"),
            bua11=row.get("bua11"),
            buasd11=row.get("buasd11"),
            ru11ind=row.get("ru11ind"),
            oac11=row.get("oac11"),
            lat=row.get("lat"),
            long=row.get("long"),
            lep1=row.get("lep1"),
            lep2=row.get("lep2"),
            pfa=row.get("pfa"),
            imd=row.get("imd"),
            calncv=row.get("calncv"),
            stp=row.get("stp"),
        )

    def add_record(self, **kwargs):
        self.records.append(Postcode(**kwargs))
        if len(self.records) >= self.bulk_limit:
            self.commit_records()

    def commit_records(self):
        self.object_count += len(self.records)
        self.logger.info("Saving {:,.0f} records".format(len(self.records)))
        Postcode.objects.bulk_create(self.records)
        self.logger.info(
            "Saved {:,.0f} records ({:,.0f} total)".format(
                len(self.records),
                self.object_count,
            )
        )
        self.records = []

    def close_spider(self):
        self.commit_records()
        self.scrape.items = self.object_count
        results = {"records": self.object_count}
        self.scrape.errors = self.error_count
        self.scrape.result = results
        self.scrape_logger.teardown()
