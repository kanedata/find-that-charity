import os
import json
import copy

from django.utils.text import slugify

with open(os.path.join(os.path.dirname(__file__), 'query.json')) as a:
    RECONCILE_QUERY = json.load(a)


def do_reconcile_query(query, orgtype='all', type='/Organization', limit=5, properties=[], type_strict='should'):
    if not query:
        return []

    if not isinstance(orgtype, list) and orgtype != "all":
        orgtype = orgtype.split("+")

    def normalise_name(n):
        stopwords = ["the", "of", "in", "uk", "ltd", "limited"]
        n = slugify(n)
        return " ".join(
            [w for w in n.split("-") if w not in stopwords]
        )

    properties = {p['pid']: p['v'] for p in properties}

    query_template, params = recon_query(
        query,
        orgtype=orgtype,
        postcode=properties.get("postalCode"),
        domain=properties.get("domain"),
    )
    q = FullOrganisation.search().from_dict(query_template)[:limit]
    result = q.execute(params=params)

    return [{
        "id": o.org_id,
        "name": "{}{}".format(
            o.name,
            "" if o.active else " [INACTIVE]",
        ),
        "type": "/Organization",
        "score": o.meta.score,
        "match": (normalise_name(o.name) == normalise_name(query)) and (o.meta.score == result.hits.max_score) and (k == 0),
    } for k, o in enumerate(result)]


def do_extend_query(ids, properties):
    result = {
        "meta": [],
        "rows": {}
    }
    all_fields = {
        f["id"]: f
        for f in Organisation.get_fields_as_properties()
    }
    fields = [p["id"] for p in properties if p["id"] in all_fields.keys()]
    result["meta"] = [all_fields[f] for f in fields]
    for r in Organisation.objects.filter(org_id__in=ids).values("org_id", *fields):
        result["rows"][r['org_id']] = {
            k: v for k, v in r.items() if k in fields}

    # add in rows for any data that is missing
    for i in ids:
        if i not in result["rows"]:
            result["rows"][i] = {k: None for k in fields}

    return result


def recon_query(term, orgtype='all', postcode=None, domain=None):
    """
    Fetch the reconciliation query and insert the query term
    """
    json_q = copy.deepcopy(RECONCILE_QUERY)
    params = {
        param: term
        for param in json_q["params"]
    }

    # add postcode
    if postcode:
        json_q["inline"]["query"]["function_score"]["functions"].append({
            "filter": {
                "match": {
                    "postalCode": "{{postcode}}"
                }
            },
            "weight": 2
        })
        params["postcode"] = postcode

    # add domain searching
    if domain:
        json_q["inline"]["query"]["function_score"]["functions"].append({
            "filter": {
                "term": {
                    "domain": "{{domain}}"
                }
            },
            "weight": 200000
        })
        params["domain"] = domain

    # check for organisation type
    if orgtype and orgtype != "all":
        if not isinstance(orgtype, list):
            orgtype = [orgtype]
        dis_max = json_q["inline"]["query"]["function_score"]["query"]
        json_q["inline"]["query"]["function_score"]["query"] = {
            "bool": {
                "must": dis_max,
                "filter": {
                    "terms": {"organisationType": orgtype}
                }
            }
        }

    return (json_q["inline"], params)


def autocomplete_query(term, orgtype='all'):
    """
    Look up an organisation using the first part of the name
    """
    doc = {
        "suggest": {
            "suggest-1": {
                "prefix": term,
                "completion": {
                    "field": "complete_names",
                    "fuzzy": {
                        "fuzziness": 1
                    }
                }
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
