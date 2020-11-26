import csv

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt

from charity.models import Charity
from ftc.documents import FullOrganisation
from ftc.models import (Organisation, OrganisationType, RelatedOrganisation,
                        Source)
from ftc.query import OrganisationSearch, random_query


# site homepage
def index(request):
    if "q" in request.GET:
        return org_search(request)

    context = dict(
        examples={
            "registered-charity-england-and-wales": "GB-CHC-1177548",
            "registered-charity-scotland": "GB-SC-SC007427",
            "registered-charity-northern-ireland": "GB-NIC-104226",
            "community-interest-company": "GB-COH-08255580",
            "local-authority": "GB-LAE-IPS",
            "universities": "GB-EDU-133808",
        },
        term="",
    )
    return render(request, "index.html.j2", context)


def about(request):
    context = {}
    return render(request, "about.html.j2", context)


def org_search(request):

    s = OrganisationSearch()
    term = None

    if "q" in request.GET:
        term = request.GET["q"].strip()
        s.set_criteria(term=term)
    if "orgtype" in request.GET and request.GET.get("orgtype") != "all":
        s.set_criteria(base_orgtype=request.GET.get("orgtype"))

    s.run_es(with_pagination=True, with_aggregation=False)
    page_number = request.GET.get("page")
    page_obj = s.paginator.get_page(page_number)

    return render(
        request,
        "search.html.j2",
        {
            "res": page_obj,
            "term": term,
            "selected_org_type": request.GET.get("orgtype"),
        },
    )


@xframe_options_exempt
def get_orgid(request, org_id, filetype="html", preview=False, as_charity=False):
    try:
        org = Organisation.objects.get(org_id=org_id)
    except Organisation.DoesNotExist:
        orgs = list(Organisation.objects.filter(orgIDs__contains=[org_id]))
        if orgs:
            orgs = RelatedOrganisation(orgs)
            org = orgs.records[0]
        else:
            raise Http404("No Organisation found.")
    if filetype == "json":
        return JsonResponse(RelatedOrganisation([org]).to_json(as_charity))

    charity = Charity.objects.filter(id=org_id).first()
    related_orgs = list(Organisation.objects.filter(linked_orgs__contains=[org_id]))
    if not related_orgs:
        related_orgs = [org]
    related_orgs = RelatedOrganisation(related_orgs)

    template = "org.html.j2"
    if preview:
        template = "org_preview.html.j2"
    elif settings.DEBUG:
        template = "charity.html.j2" if charity else "org.html.j2"

    return render(
        request,
        template,
        {
            "org": org,
            "related_orgs": related_orgs,
            "charity": charity,
        },
    )


@xframe_options_exempt
def get_orgid_canon(request, org_id):

    related_orgs = list(Organisation.objects.filter(linked_orgs__contains=[org_id]))
    if not related_orgs:
        raise Http404("No Organisation found.")
    related_orgs = RelatedOrganisation(related_orgs)

    return JsonResponse(related_orgs.to_json())


def get_random_org(request):
    """Get a random charity record"""
    # filetype = request.GET.get("filetype", "html")
    active = request.GET.get("active", False)
    q = FullOrganisation.search().from_dict(random_query(active, "registered-charity"))[
        0
    ]
    result = q.execute()
    for r in result:
        return JsonResponse(r.__dict__["_d_"])


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    query = {
        "orgtype": [],
        "source": [],
        "q": None,
        "include_inactive": False,
    }
    s = OrganisationSearch()
    term = None

    if orgtype:
        query["base_query"] = get_object_or_404(OrganisationType, slug=orgtype)
        query["orgtype"].append(orgtype)
        s.set_criteria(base_orgtype=orgtype)
        download_url = reverse("orgid_type_download", kwargs={"orgtype": orgtype})
    elif source:
        query["base_query"] = get_object_or_404(Source, id=source)
        query["source"].append(source)
        download_url = reverse("orgid_source_download", kwargs={"source": source})
    if request.GET:
        download_url += "?" + request.GET.urlencode()

    # add additional criteria from the get params
    if "orgtype" in request.GET:
        query["orgtype"].extend(request.GET.getlist("orgtype"))
        s.set_criteria(other_orgtypes=request.GET.getlist("orgtype"))
    if "source" in request.GET:
        query["source"].extend(request.GET.getlist("source"))
    if "q" in request.GET:
        term = request.GET["q"].strip()
        query["q"] = term
        s.set_criteria(term=query["q"])
    if request.GET.get("inactive") == "include_inactive":
        query["include_inactive"] = True

    # convert query to criteria
    s.set_criteria(source=query["source"])
    if not query.get("include_inactive") and filetype != "csv":
        s.set_criteria(active=True)

    if filetype == "csv":
        columns = {
            "org_id": "id",
            "name": "name",
            "charityNumber": "charityNumber",
            "companyNumber": "companyNumber",
            "postalCode": "postalCode",
            "url": "url",
            "latestIncome": "latestIncome",
            "latestIncomeDate": "latestIncomeDate",
            "dateRegistered": "dateRegistered",
            "dateRemoved": "dateRemoved",
            "active": "active",
            "dateModified": "dateModified",
            "orgIDs": "orgIDs",
            "organisationType": "organisationType",
            "organisationTypePrimary__title": "organisationTypePrimary",
            "source": "source",
        }
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(
            query["base_query"].slug
        )
        writer = csv.writer(response)
        writer.writerow(columns.values())
        s.run_db()
        res = s.query.values_list(*columns.keys()).order_by("org_id")
        for r in res:
            writer.writerow(r)
        return response

    s.run_es(with_pagination=True, with_aggregation=True)
    page_number = request.GET.get("page")
    page_obj = s.paginator.get_page(page_number)

    return render(
        request,
        "orgtype.html.j2",
        {
            "res": page_obj,
            "query": query,
            "term": term,
            "aggs": {
                "by_orgtype": s.aggregation.get("by_orgtype"),
                "by_source": s.aggregation.get("by_source"),
            },
            "download_url": download_url,
        },
    )
