from django.shortcuts import get_object_or_404, render
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

    s = CompanyDocument.search().from_dict(search_dict)
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
