from django.shortcuts import render, get_object_or_404

from companies.models import Company


def company_detail(request, company_number, filetype="html"):
    company = get_object_or_404(Company, CompanyNumber=company_number)
    return render(request, "companies/company_detail.html.j2", {"company": company, "heading": "Company | {}".format(company.CompanyName)})
