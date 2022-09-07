import psycopg2
from django.conf import settings
from tqdm import tqdm

from ftc.management.commands._base_scraper import BaseScraper
from other_data.models import Grant

QUERY = """
select g.data->>'id' as "grant_id",
  g.data->>'title' as "title",
  g.data->>'description' as "description",
  g.data->>'currency' as "currency",
  g.data->>'amountAwarded' as "amountAwarded",
  g.data->>'awardDate' as "awardDate",
  g.data->'recipientOrganization'->0->>'id' as "recipientOrganization_id",
  g.data->'recipientOrganization'->0->>'name' as "recipientOrganization_name",
  g.data->'fundingOrganization'->0->>'id' as "fundingOrganization_id",
  g.data->'fundingOrganization'->0->>'name' as "fundingOrganization_name",
  g.source_data->'publisher'->>'prefix' as "publisher_prefix",
  g.source_data->'publisher'->>'name' as "publisher_name",
  g.source_data->>'license' as "license"
from view_latest_grant g
"""


class Command(BaseScraper):
    name = "360g"
    float_fields = [
        "AwardAmount",
    ]
    date_fields = ["awardDate"]
    source = {
        "title": "360Giving",
        "description": "",
        "identifier": "360g",
        "license": "",
        "license_name": "",
        "issued": "",
        "modified": "",
        "publisher": {
            "name": "360Giving",
            "website": "https://threesixtygiving.org.uk/",
        },
        "distribution": [
            {
                "downloadURL": "",
                "accessURL": "https://grantnav.threesixtygiving.org.uk/",
                "title": "Download Grant Data",
            }
        ],
    }
    models_to_delete = [Grant]
    query = QUERY

    def add_arguments(self, parser):
        parser.add_argument(
            "--db-con",
            default=settings.DATASTORE_360GIVING_URL,
            help="Database connection string",
        )

    def run_scraper(self, *args, **options):
        self.post_sql = {}

        # setup database connection
        self.logger.info("Connecting to database")
        self.tsg_connection = psycopg2.connect(options["db_con"])
        self.tsg_cursor = self.tsg_connection.cursor()

        # run the query
        self.logger.info("Executing query")
        self.tsg_cursor.execute(self.query)

        # go through and save the grants
        self.logger.info("Iterating over results")
        columns = [desc[0] for desc in self.tsg_cursor.description]
        for row in tqdm(self.tsg_cursor):
            self.parse_row(dict(zip(columns, row)))

        # close the spider
        self.close_spider()
        self.logger.info("Spider finished")

    def parse_row(self, original_row):
        original_row["awardDate"] = original_row["awardDate"][0:10]
        row = self.clean_fields(original_row)
        row["scrape"] = self.scrape
        self.add_record(Grant, row)
