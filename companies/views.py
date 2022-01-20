from django.shortcuts import get_object_or_404, render

from companies.models import Company
from ftc.models import Vocabulary, VocabularyEntries


def company_detail(request, company_number, filetype="html"):
    # company = get_object_or_404(Company, CompanyNumber=company_number)
    company = Company.objects.filter(CompanyNumber=company_number).first()

    vocab, _ = Vocabulary.objects.get_or_create(title="Companies House SIC Codes")
    sic_codes = {
        entry.code: entry
        for entry in VocabularyEntries.objects.filter(vocabulary=vocab)
    }

    return render(
        request,
        "companies/company_detail.html.j2",
        {"company": company, "heading": "Company | {}".format(company.CompanyName), "sic_codes": sic_codes},
    )
