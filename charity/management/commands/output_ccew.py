import io

from boto3 import session
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections

from charity.views import export_to_sqlite, export_to_xlsx

AREAS_QUERY = """
SELECT DISTINCT "{geo_field}" AS codes
FROM ftc_organisationlocation fo
WHERE "{geo_field}" IS NOT NULL
"""


class Command(BaseCommand):
    help = "Export excel data from CCEW for a given area"

    def add_arguments(self, parser):
        parser.add_argument("area", type=str, nargs="+", help="Area to export data for")
        parser.add_argument(
            "--filename",
            type=str,
            default="data/{geo_field}/{geocode}",
            help="Filename to export to. Don't include extension",
        )
        parser.add_argument(
            "--geo-field",
            type=str,
            default="geo_laua",
            help="Geo field to use for filtering",
        )
        parser.add_argument(
            "--filetype",
            type=str,
            default="xlsx",
            help="Filetype for export (xlsx or sqlite)",
        )
        parser.add_argument(
            "--upload-to-storage",
            action="store_true",
            help="Upload file to S3 or compatible storage after export",
        )

    def handle(self, *args, **options):
        self.cursor = connections["data"].cursor()
        self.s3_client = None

        if options["upload_to_storage"]:
            s3_session = session.Session()
            self.s3_client = s3_session.client(
                "s3",
                region_name=settings.S3_REGION,
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_ID,
                aws_secret_access_key=settings.S3_SECRET_KEY,
            )

        if "all" in options["area"]:
            self.cursor.execute(AREAS_QUERY.format(geo_field=options["geo_field"]))
            areas = [row[0] for row in self.cursor.fetchall()]
        else:
            areas = options["area"]

        if len(areas) > 1:
            if "{geocode}" not in options["filename"]:
                raise ValueError(
                    "Filename must contain {geocode} when exporting multiple areas"
                )

        for area in areas:
            filename = options["filename"].format(
                geocode=area, geo_field=options["geo_field"]
            )
            print(filename)
            if options["filetype"] == "xlsx":
                filename += ".xlsx"
                data = export_to_xlsx(options["geo_field"], area)
            elif options["filetype"] == "sqlite":
                filename += ".sqlite"
                data = export_to_sqlite(options["geo_field"], area)
            else:
                raise ValueError("Invalid filetype")

            if self.s3_client:
                self.s3_client.upload_fileobj(
                    io.BytesIO(data),
                    settings.S3_BUCKET,
                    filename,
                    ExtraArgs={"ACL": "public-read"},
                )
                print(f"{filename} uploaded to s3")
            else:
                with open(filename, "wb") as f:
                    f.write(data)
                print(f"{filename} saved")
