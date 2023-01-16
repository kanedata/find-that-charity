import json
import urllib.parse

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, reverse
from django.utils.text import slugify
from django.views.decorators.clickjacking import xframe_options_exempt

from companies.documents import CompanyDocument
from companies.models import Company
from findthatcharity.utils import normalise_name, to_titlecase
from ftc.models import (
    Organisation,
    RelatedOrganisation,
    Source,
    Vocabulary,
    VocabularyEntries,
)

COMPANY_RECON_TYPE = {"id": "/registered-company", "name": "Registered Company"}


@xframe_options_exempt
def company_detail(request, company_number, filetype="html"):
    company = get_object_or_404(Company, CompanyNumber=company_number)

    vocab = Vocabulary.objects.get(title="Companies House SIC Codes")
    sic_codes = {
        entry.code: entry
        for entry in VocabularyEntries.objects.filter(vocabulary=vocab)
    }

    # fetch any related organisations
    org = None
    orgs = list(Organisation.objects.filter(orgIDs__contains=[company.org_id]))
    if orgs:
        orgs = RelatedOrganisation(orgs)
        org = orgs.records[0]

    return render(
        request,
        "companies/company_detail.html.j2",
        {
            "company": company,
            "heading": "Company {} | {}".format(
                company.CompanyNumber,
                company.CompanyName,
            ),
            "sic_codes": sic_codes,
            "source": Source.objects.get(id="companies"),
            "org": org,
        },
    )


def company_reconcile(request):

    queries = request.POST.get("queries", request.GET.get("queries"))
    if queries:
        queries = json.loads(queries)
        results = {}
        for query_id, query in queries.items():
            results[query_id] = do_reconcile_query(**query)
        return JsonResponse(results)

    return JsonResponse(service_spec(request))


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

    properties = {p["pid"]: p["v"] for p in properties}

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

    s = CompanyDocument.search().from_dict(search_dict)
    result = s.execute()

    return {
        "result": [
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
        "normalised_query": normalise_name(query),
    }


def service_spec(request):
    """Return the default service specification

    Specification found here: https://github.com/OpenRefine/OpenRefine/wiki/Reconciliation-Service-API#service-metadata
    """

    return {
        "name": "Find that Charity Company Reconciliation API",
        "identifierSpace": "http://org-id.guide",
        "schemaSpace": "https://schema.org",
        "view": {
            "url": urllib.parse.unquote(
                request.build_absolute_uri(
                    reverse("company_detail", kwargs={"company_number": "{{id}}"})
                )
            )
        },
        "preview": {
            "url": urllib.parse.unquote(
                request.build_absolute_uri(
                    reverse("company_detail", kwargs={"company_number": "{{id}}"})
                )
            ),
            "width": 430,
            "height": 300,
        },
        "defaultTypes": [COMPANY_RECON_TYPE],
    }
