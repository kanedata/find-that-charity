import json
import os
import copy

from django.http import JsonResponse, Http404
from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt
from elasticsearch_dsl.query import MultiMatch, Match
from django.utils.text import slugify

from ftc.models import Organisation
from ftc.documents import FullOrganisation


with open(os.path.join(os.path.dirname(__file__), 'query.json')) as a:
    RECONCILE_QUERY = json.load(a)


@csrf_exempt
def index(request, orgtype='all'):

    queries = request.POST.get("queries", request.GET.get("queries"))
    if queries:
        queries = json.loads(queries)
        results = {}
        for query_id, query in queries.items():
            results[query_id] = do_reconcile_query(**query, orgtype=orgtype)
        return JsonResponse(results)

    extend = request.POST.get("extend", request.GET.get("extend"))
    if extend:
        extend = json.loads(extend)
        return JsonResponse(do_extend_query(**extend))

    return JsonResponse(service_spec(request))


def service_spec(request):
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """
    return {
        "name": "Find that Charity Reconciliation API",
        "identifierSpace": "http://org-id.guide",
        "schemaSpace": "https://schema.org",
        "view": {
            "url": request.build_absolute_uri(
                reverse('orgid_html', kwargs={'org_id': '{{id}}'})
            )
        },
        "preview": {
            "url": request.build_absolute_uri(
                reverse('orgid_html_preview', kwargs={'org_id': '{{id}}'})
            ),
            "width": 430,
            "height": 300
        },
        "defaultTypes": [{
            "id": "/Organization",
            "name": "Organisation",
        }],
        "extend": {
            "propose_properties": {
                "service_url": request.build_absolute_uri(reverse('index')),
                "service_path": "/reconcile/propose_properties"
            },
            "property_settings": []
        },
    }


def do_reconcile_query(query, orgtype='all', type='/Organization', limit=5, properties=[], type_strict='should'):
    if not query:
        return []

    if orgtype != "all":
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
        result["rows"][r['org_id']] = {k: v for k, v in r.items() if k in fields}

    # add in rows for any data that is missing
    for i in ids:
        if i not in result["rows"]:
            result["rows"][i] = {k: None for k in fields}

    return result


def recon_query(term, orgtype='all', postcode=None):
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


def propose_properties(request):
    type_ = request.GET.get("type", "Organization")
    if type_ != "Organization":
        raise Http404("type must be Organization")

    limit = int(request.GET.get("limit", "500"))

    return JsonResponse({
        "limit": limit,
        "type": type_,
        "properties": Organisation.get_fields_as_properties(),
    })
