from django.shortcuts import get_object_or_404, render

from companies.models import Company
from ftc.models import (
    Organisation,
    RelatedOrganisation,
    Source,
    Vocabulary,
    VocabularyEntries,
)


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
