import io

import xlsxwriter
from django.http import HttpResponse
from django.shortcuts import redirect

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


def get_charity(request, regno, filetype="html", preview=False):
    org_id = regno_to_orgid(regno)

    if filetype == "html":
        return redirect("orgid_html", org_id=org_id, permanent=True)

    return get_org_by_id(request, org_id, filetype, preview, as_charity=True)


def export_data(request, geoarea, geocode, filetype="html"):
    geoareas = {
        "la": "geo_laua",
        "rgn": "geo_rgn",
    }
    geoarea = geoareas.get(geoarea.lower(), "geo_laua")

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

    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        buffer,
        {"default_date_format": "yyyy-mm-dd", "in_memory": True},
    )
    for table in ccew_tables:
        query = base_query.format(charity_table=table._meta.db_table, geo_field=geoarea)
        print(f"Exporting {table._meta.db_table}")
        worksheet = workbook.add_worksheet(
            table._meta.db_table.replace("charity_ccew", "")
        )

        columns = [
            column.name for column in table._meta.get_fields() if column.name != "id"
        ]
        table_data = []

        for row_index, row in enumerate(table.objects.raw(query, {"area": geocode})):
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

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f"attachment; filename=ccew_export_{geocode}.xlsx"
    return response
