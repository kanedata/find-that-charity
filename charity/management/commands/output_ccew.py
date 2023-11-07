import xlsxwriter
from django.core.management.base import BaseCommand

from charity.models import (
    CCEWCharity,
    CCEWCharityAnnualReturnHistory,
    CCEWCharityAreaOfOperation,
    CCEWCharityARPartA,
    CCEWCharityARPartB,
    CCEWCharityClassification,
    CCEWCharityEventHistory,
    CCEWCharityGoverningDocument,
    CCEWCharityOtherNames,
    CCEWCharityOtherRegulators,
    CCEWCharityPolicy,
    CCEWCharityPublishedReport,
    CCEWCharityTrustee,
)


class Command(BaseCommand):
    help = "Export excel data from CCEW for a given area"
    ccew_tables = [
        CCEWCharity,
        CCEWCharityAnnualReturnHistory,
        CCEWCharityAreaOfOperation,
        CCEWCharityARPartA,
        CCEWCharityARPartB,
        CCEWCharityClassification,
        CCEWCharityEventHistory,
        CCEWCharityGoverningDocument,
        CCEWCharityOtherNames,
        CCEWCharityOtherRegulators,
        CCEWCharityPolicy,
        CCEWCharityPublishedReport,
        CCEWCharityTrustee,
    ]

    def add_arguments(self, parser):
        parser.add_argument("area", type=str, help="Area to export data for")
        parser.add_argument("filename", type=str, help="Filename to export to")
        parser.add_argument(
            "--geo-field",
            type=str,
            default="geo_laua",
            help="Geo field to use for filtering",
        )

    def handle(self, *args, **options):
        base_query = """
        WITH a AS (
            SELECT DISTINCT replace(org_id, 'GB-CHC-', '')::INTEGER AS charity_number
            FROM ftc_organisationlocation fo 
            WHERE "org_id" LIKE 'GB-CHC-%%'
                AND "{geo_field}" = %(area)s
        )
        SELECT c.*
        FROM "{charity_table}" c
        INNER JOIN a
        ON c.registered_charity_number = a.charity_number
        """

        workbook = xlsxwriter.Workbook(
            options["filename"], {"default_date_format": "yyyy-mm-dd"}
        )
        for table in self.ccew_tables:
            query = base_query.format(
                charity_table=table._meta.db_table, geo_field=options["geo_field"]
            )
            self.stdout.write(f"Exporting {table._meta.db_table}")
            worksheet = workbook.add_worksheet(
                table._meta.db_table.replace("charity_ccew", "")
            )

            columns = [
                column.name
                for column in table._meta.get_fields()
                if column.name != "id"
            ]
            table_data = []

            for row_index, row in enumerate(
                table.objects.raw(query, {"area": options["area"]})
            ):
                record = {
                    k: v for k, v in row.__dict__.items() if k not in ("_state", "id")
                }
                table_data.append([record.get(column, "") for column in columns])

            if len(table_data) == 0:
                table_data = [[None for _ in columns]]

            worksheet.add_table(
                0,
                0,
                len(table_data),
                len(columns) - 1,
                {
                    "data": table_data,
                    "columns": [
                        {
                            "header": column,
                        }
                        for column in columns
                    ],
                    "name": table._meta.db_table.replace("charity_ccew", ""),
                },
            )
            worksheet.autofit()

        workbook.close()
