from charity_django.utils.text import to_titlecase
from django.utils.text import slugify

from findthatcharity.utils import normalise_name
from ftc.documents import CompanyDocument

COMPANY_RECON_TYPE = {"id": "/registered-company", "name": "Registered Company"}


def do_reconcile_query(
    query,
    orgtypes="all",
    type="/Organization",
    limit=5,
    properties=[],
    type_strict="should",
    result_key="result",
):
    if not query:
        return []

    properties = {p["pid"]: p["v"] for p in properties} if properties else {}

    search_dict = {
        "query": {
            "query_string": {
                "query": query,
                "fields": ["CompanyName^2", "CompanyNumber^5", "PreviousNames"],
            }
        },
        "size": limit,
    }

    if properties.get("postcode"):
        # boost the score if the postcode matches
        search_dict["query"] = {
            "function_score": {
                "query": search_dict["query"],
                "functions": [
                    {
                        "filter": {
                            "match": {"RegAddress_PostCode": properties["postcode"]}
                        },
                        "weight": 1.5,
                    }
                ],
                "boost_mode": "multiply",
            }
        }

    s = CompanyDocument.search().update_from_dict(search_dict)
    result = s.execute()

    return {
        result_key: [
            {
                "id": o.CompanyNumber,
                "name": "{} ({}){}".format(
                    to_titlecase(o.CompanyName),
                    o.CompanyNumber,
                    "" if o.CompanyStatus == "Active" else " [INACTIVE]",
                ),
                "type": [COMPANY_RECON_TYPE]
                + [
                    {
                        "id": "/{}".format(slugify(o.CompanyCategory)),
                        "name": o.CompanyCategory,
                    }
                ],
                "score": o.meta.score,
                "match": (normalise_name(o.CompanyName) == normalise_name(query))
                and (o.meta.score == result.hits.max_score)
                and (k == 0),
            }
            for k, o in enumerate(result)
        ],
    }
