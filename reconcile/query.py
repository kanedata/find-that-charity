import copy
import json
import os

from django.utils.text import slugify

from findthatcharity.jinja2 import get_orgtypes
from findthatcharity.utils import to_titlecase
from ftc.documents import FullOrganisation
from ftc.models import Organisation

with open(os.path.join(os.path.dirname(__file__), "query.json")) as a:
    RECONCILE_QUERY = json.load(a)


def do_reconcile_query(
    query,
    orgtypes="all",
    type="/Organization",
    limit=5,
    properties=[],
    type_strict="should",
):
    if not query:
        return []

    if not isinstance(orgtypes, list) and orgtypes != "all":
        orgtypes = orgtypes.split("+")

    def normalise_name(n):
        stopwords = ["the", "of", "in", "uk", "ltd", "limited"]
        n = slugify(n)
        return " ".join([w for w in n.split("-") if w not in stopwords])

    properties = {p["pid"]: p["v"] for p in properties}

    query_template, params = recon_query(
        query,
        orgtypes=orgtypes,
        postcode=properties.get("postalCode"),
        domain=properties.get("domain"),
    )
    q = FullOrganisation.search().from_dict(query_template)[:limit]
    result = q.execute(params=params)
    all_orgtypes = get_orgtypes()

    return {
        "result": [
            {
                "id": o.org_id,
                "name": "{} ({}){}".format(
                    to_titlecase(o.name),
                    o.org_id,
                    "" if o.active else " [INACTIVE]",
                ),
                "type": [{
                    "id": o.organisationTypePrimary,
                    "name": all_orgtypes[o.organisationTypePrimary].title,
                }],
                "score": o.meta.score,
                "match": (normalise_name(o.name) == normalise_name(query))
                and (o.meta.score == result.hits.max_score)
                and (k == 0),
            }
            for k, o in enumerate(result)
        ]
    }


def do_extend_query(ids, properties):
    result = {"meta": [], "rows": {}}
    all_fields = {f["id"]: f for f in Organisation.get_fields_as_properties()}
    fields = [p["id"] for p in properties if p["id"] in all_fields.keys()]
    result["meta"] = [all_fields[f] for f in fields]
    for r in Organisation.objects.filter(org_id__in=ids).values("org_id", *fields):
        result["rows"][r["org_id"]] = {k: v for k, v in r.items() if k in fields}

    # add in rows for any data that is missing
    for i in ids:
        if i not in result["rows"]:
            result["rows"][i] = {k: None for k in fields}

    return result


def recon_query(
    term=None,
    orgtypes="all",
    other_orgtypes=None,
    postcode=None,
    domain=None,
    source=None,
):
    """
    Fetch the reconciliation query and insert the query term
    """
    json_q = copy.deepcopy(RECONCILE_QUERY)

    params = {}

    if term:
        for param in json_q["params"]:
            params[param] = term
    else:
        json_q["inline"]["query"]["function_score"]["query"]["bool"]["must"] = {
            "match_all": {}
        }

    # add postcode
    if postcode:
        json_q["inline"]["query"]["function_score"]["functions"].append(
            {"filter": {"match": {"postalCode": "{{postcode}}"}}, "weight": 2}
        )
        params["postcode"] = postcode

    # add domain searching
    if domain:
        json_q["inline"]["query"]["function_score"]["functions"].append(
            {"filter": {"term": {"domain": "{{domain}}"}}, "weight": 200000}
        )
        params["domain"] = domain

    # check for organisation type
    filter_ = []
    if orgtypes and orgtypes != "all":
        if not isinstance(orgtypes, list):
            orgtypes = [orgtypes]
        filter_.append({"terms": {"organisationType": [o.slug for o in orgtypes]}})

    # check for source
    if source:
        filter_.append({"term": {"source": source}})

    if filter_:
        json_q["inline"]["query"]["function_score"]["query"]["bool"]["filter"] = filter_

    return (json_q["inline"], params)


def autocomplete_query(term, orgtype="all"):
    """
    Look up an organisation using the first part of the name
    """
    doc = {
        "suggest": {
            "suggest-1": {
                "prefix": term,
                "completion": {"field": "complete_names", "fuzzy": {"fuzziness": 1}},
            }
        }
    }

    # if not orgtype or orgtype == 'all':
    #     orgtype = [o.slug for o in OrganisationType.objects.all()]
    # elif orgtype:
    #     orgtype = orgtype.split("+")

    # doc["suggest"]["suggest-1"]["completion"]["contexts"] = {
    #     "organisationType": orgtype
    # }

    return doc
