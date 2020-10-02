import json
import urllib.parse

from django.http import Http404, JsonResponse
from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt

from findthatcharity.jinja2 import get_orgtypes
from ftc.documents import FullOrganisation
from ftc.models import Organisation
from reconcile.query import do_extend_query, do_reconcile_query


@csrf_exempt
def index(request, orgtype="all"):

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
            "url": urllib.parse.unquote(
                request.build_absolute_uri(
                    reverse("orgid_html", kwargs={"org_id": "{{id}}"})
                )
            )
        },
        "preview": {
            "url": urllib.parse.unquote(
                request.build_absolute_uri(
                    reverse("orgid_html_preview", kwargs={"org_id": "{{id}}"})
                )
            ),
            "width": 430,
            "height": 300,
        },
        "defaultTypes": [{"id": "/Organization", "name": "Organisation"}],
        "extend": {
            "propose_properties": {
                "service_url": request.build_absolute_uri(reverse("index")),
                "service_path": reverse("propose_properties"),
            },
            "property_settings": [],
        },
        "suggest": {
            "entity": {
                "service_url": request.build_absolute_uri(reverse("index")),
                "service_path": reverse("suggest"),
                # "flyout_service_path": "/suggest/flyout/${id}"
            }
        },
    }


@csrf_exempt
def propose_properties(request):
    type_ = request.GET.get("type", "Organization")
    if type_ != "Organization":
        raise Http404("type must be Organization")

    limit = int(request.GET.get("limit", "500"))

    return JsonResponse(
        {
            "limit": limit,
            "type": type_,
            "properties": Organisation.get_fields_as_properties(),
        }
    )


@csrf_exempt
def suggest(request, orgtype="all"):
    SUGGEST_NAME = "name_complete"

    prefix = request.GET.get("prefix")
    # cursor = request.GET.get("cursor")
    if not prefix:
        raise Http404("Prefix must be supplied")
    q = FullOrganisation.search()

    completion = {"field": "complete_names", "fuzzy": {"fuzziness": 1}}
    if orgtype and orgtype != "all":
        completion["contexts"] = dict(organisationType=orgtype.split("+"))
    else:
        orgtypes = get_orgtypes()
        completion["contexts"] = dict(organisationType=[
            o for o in orgtypes.keys()
        ])

    q = q.suggest(SUGGEST_NAME, prefix, completion=completion).source(
        ["org_id", "name", "organisationType"]
    )
    result = q.execute()

    return JsonResponse(
        {
            "result": [
                {
                    "id": r["_source"]["org_id"],
                    "name": r["_source"]["name"],
                    "url": request.build_absolute_uri(
                        reverse("orgid_html", kwargs={"org_id": r["_source"]["org_id"]})
                    ),
                    "orgtypes": list(r["_source"]["organisationType"]),
                }
                for r in result.suggest[SUGGEST_NAME][0]["options"]
            ]
        }
    )
