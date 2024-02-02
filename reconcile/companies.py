from charity_django.utils.text import to_titlecase
from django.utils.text import slugify

from findthatcharity.utils import normalise_name
from ftc.documents import CompanyDocument

COMPANY_RECON_TYPE = {"id": "/registered-company", "name": "Registered Company"}


def do_reconcile_query(
    query,
    orgtypes="all",
    type_="/Organization",
    limit=5,
    properties=[],
    type_strict="should",
    result_key="result",
):
    if not query:
        return {result_key: []}

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


def do_extend_query(ids, properties):
    all_fields = [p["id"] for p in properties]
    result = {"meta": [{"id": p, "name": p} for p in all_fields], "rows": {}}

    ids_map = {id: id.replace("GB-COH-", "") for id in ids}

    # get the data
    lookup_results = {
        doc.meta.id: doc
        for doc in CompanyDocument.mget(ids_map.values(), _source_includes=all_fields)
        if doc
    }

    # clean up the data
    for id in ids:
        lookup_result = lookup_results.get(ids_map[id])
        if not lookup_result:
            result["rows"][id] = {k: None for k in all_fields}
            continue
        result["rows"][id] = {k: lookup_result[k] for k in all_fields}

    return result
