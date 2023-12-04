import io
import os
from tempfile import NamedTemporaryFile

import xlsxwriter
from django.shortcuts import redirect
from sqlite_utils import Database

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
from charity.utils import regno_to_orgid
from ftc.views import get_org_by_id

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


GEOAREAS = {
    "la": "geo_laua",
    "rgn": "geo_rgn",
}


def get_charity(request, regno, filetype="html", preview=False):
    org_id = regno_to_orgid(regno)

    if filetype == "html":
        return redirect("orgid_html", org_id=org_id, permanent=True)

    return get_org_by_id(request, org_id, filetype, preview, as_charity=True)


def get_export_data(geofield, geocode):
    base_query = """
        WITH a AS (
            SELECT DISTINCT replace(org_id, 'GB-CHC-', '')::INTEGER AS charity_number
            FROM ftc_organisationlocation fo 
            WHERE "org_id" LIKE 'GB-CHC-%%'
                AND "{geo_field}" IN %(area)s
        )
        SELECT c.*
        FROM "{charity_table}" c
        INNER JOIN a
        ON c.registered_charity_number = a.charity_number
        """

    for table in ccew_tables:
        query = base_query.format(
            charity_table=table._meta.db_table, geo_field=geofield
        )
        print(f"Exporting {table._meta.db_table}")

        columns = [
            column.name for column in table._meta.get_fields() if column.name != "id"
        ]
        table_data = []

        for row_index, row in enumerate(
            table.objects.raw(query, {"area": tuple(geocode.split("+"))})
        ):
            record = {
                k: v for k, v in row.__dict__.items() if k not in ("_state", "id")
            }
            table_data.append([record.get(column, "") for column in columns])

        yield table, columns, table_data


def export_to_xlsx(geoarea, geocode):
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        buffer,
        {"default_date_format": "yyyy-mm-dd", "in_memory": True},
    )

    for table, columns, table_data in get_export_data(geoarea, geocode):
        if len(table_data) == 0:
            table_data = [[None for _ in columns]]

        worksheet = workbook.add_worksheet(
            table._meta.db_table.replace("charity_ccew", "")
        )
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
    return buffer.getvalue()


def export_to_sqlite(geoarea, geocode):
    # create a temporary file
    tmpfile = NamedTemporaryFile(suffix=".db", delete=False)
    tmpfile.close()

    db = Database(tmpfile.name)

    for table, columns, table_data in get_export_data(geoarea, geocode):
        db_table = db[table._meta.db_table.replace("charity_ccew", "")]
        db_table.insert_all([dict(zip(columns, row)) for row in table_data])
    db.close()

    with open(tmpfile.name, "rb") as output_file:
        data = output_file.read()

    os.unlink(tmpfile.name)
    return data


def export_data(request, geoarea, geocode, filetype="xlsx"):
    geoarea = GEOAREAS.get(geoarea.lower(), "geo_laua")
    s3_file_url = "https://findthatcharity.ams3.cdn.digitaloceanspaces.com/findthatcharity/data/{geoarea}/{geocode}.{filetype}".format(
        geoarea=geoarea, geocode=geocode, filetype=filetype
    )
    return redirect(s3_file_url, permanent=True)
