import json

from django.http import JsonResponse
from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt

from ftc.models import Organisation


@csrf_exempt
def index(request):

    queries = request.POST.get("queries", request.GET.get("queries"))
    if queries:
        queries = json.loads(queries)
        results = {}
        for query_id, query in queries.items():
            results[query_id] = reconcile_query(**query)
        return JsonResponse(results)

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
        }]
    }


def reconcile_query(query, type='/Organization', limit=5, properties=[], type_strict='should'):
    if not query:
        return []

    orgs = Organisation.objects.filter(name__search=query)[0:limit]
    return [{
        "id": o.org_id,
        "name": o.name,
        "type": "/Organization",
        "score": 0,
        "match": False,
    } for o in orgs]
