import json
import urllib.parse

from django.http import Http404, JsonResponse
from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt

from findthatcharity.jinja2 import get_orgtypes
from ftc.documents import OrganisationGroup
from ftc.models import Organisation, OrganisationType, Vocabulary
from reconcile.query import do_extend_query, do_reconcile_query


@csrf_exempt
def index(request, orgtype="all"):

    if orgtype == "all":
        orgtypes = []
    elif isinstance(orgtype, str):
        orgtypes = [OrganisationType.objects.get(slug=o) for o in orgtype.split("+")]
    elif isinstance(orgtype, list):
        orgtypes = [OrganisationType.objects.get(slug=o) for o in orgtype]

    queries = request.POST.get("queries", request.GET.get("queries"))
    if queries:
        queries = json.loads(queries)
        results = {}
        for query_id, query in queries.items():
            results[query_id] = do_reconcile_query(**query, orgtypes=orgtypes)
        return JsonResponse(results)

    extend = request.POST.get("extend", request.GET.get("extend"))
    if extend:
        extend = json.loads(extend)
        return JsonResponse(do_extend_query(**extend))

    return JsonResponse(service_spec(request, orgtypes=orgtypes))


def service_spec(request, orgtypes=None):
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """

    if not orgtypes or orgtypes == "all":
        defaultTypes = [{"id": "/Organization", "name": "Organisation"}]
    elif isinstance(orgtypes, list):
        defaultTypes = [{"id": o.slug, "name": o.title} for o in orgtypes]

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
        "defaultTypes": defaultTypes,
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

    organisation_properties = Organisation.get_fields_as_properties()

    vocabulary_properties = [
        {"id": "vocab-" + v.slug, "name": v.title, "group": "Vocabulary"}
        for v in Vocabulary.objects.all()
        if v.entries.count() > 0
    ]

    ccew_properties = [
        {
            "id": "ccew-parta-total_gross_expenditure",
            "name": "Total Expenditure",
            "group": "Charity",
        },
        {
            "id": "ccew-partb-count_employees",
            "name": "Number of staff",
            "group": "Charity",
        },
        {
            "id": "ccew-partb-expenditure_charitable_expenditure",
            "name": "Charitable expenditure",
            "group": "Charity",
        },
        {
            "id": "ccew-partb-expenditure_grants_institution",
            "name": "Grantmaking expenditure",
            "group": "Charity",
        },
        {
            "id": "ccew-gd-charitable_objects",
            "name": "Objects",
            "group": "Charity",
        },
        {
            "id": "ccew-aoo-geographic_area_description",
            "name": "Area of Operation",
            "group": "Charity",
        },
    ]

    return JsonResponse(
        {
            "limit": limit,
            "type": type_,
            "properties": organisation_properties
            + vocabulary_properties
            + ccew_properties,
        }
    )


@csrf_exempt
def suggest(request, orgtype=None):
    SUGGEST_NAME = "name_complete"

    prefix = request.GET.get("prefix")
    # cursor = request.GET.get("cursor")
    if not prefix:
        raise Http404("Prefix must be supplied")
    q = OrganisationGroup.search()

    if not orgtype or orgtype == "all":
        orgtype = []
    orgtype.extend(request.GET.getlist("orgtype"))

    completion = {"field": "complete_names", "fuzzy": {"fuzziness": 1}}
    if orgtype:
        completion["contexts"] = dict(organisationType=orgtype)
    else:
        all_orgtypes = get_orgtypes()
        completion["contexts"] = dict(organisationType=[o for o in all_orgtypes.keys()])

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
