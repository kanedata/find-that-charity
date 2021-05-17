import csv

from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from elasticsearch.exceptions import RequestError

from charity.models import Charity
from ftc.documents import FullOrganisation
from ftc.models import Organisation, OrganisationType, RelatedOrganisation, Source
from ftc.query import (
    OrganisationSearch,
    get_linked_organisations,
    get_organisation,
    random_query,
)
from other_data.models import CQCProvider


# site homepage
def index(request):
    if "q" in request.GET:
        return orgid_type(request, filetype=request.GET.get("filetype", "html"))

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


@xframe_options_exempt
def get_org_by_id(request, org_id, filetype="html", preview=False, as_charity=False):
    org = get_organisation(org_id)
    if filetype == "json":
        return JsonResponse(
            RelatedOrganisation([org]).to_json(as_charity, request=request)
        )

    charity = Charity.objects.filter(id=org_id).first()
    related_orgs = list(Organisation.objects.filter(linked_orgs__contains=[org_id]))
    if not related_orgs:
        related_orgs = [org]
    related_orgs = RelatedOrganisation(related_orgs)

    cqc = CQCProvider.objects.filter(org_id=related_orgs.org_id).all()

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
            "cqc": cqc,
        },
    )


@xframe_options_exempt
def get_orgid_canon(request, org_id):
    related_orgs = get_linked_organisations(org_id)
    return JsonResponse(related_orgs.to_json(request=request))


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


# https://docs.djangoproject.com/en/3.1/howto/outputting-csv/#streaming-csv-files
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """

    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    base_query = None
    download_url = request.build_absolute_uri() + "&filetype=csv"
    s = OrganisationSearch()

    if orgtype:
        base_query = get_object_or_404(OrganisationType, slug=orgtype)
        s.set_criteria(base_orgtype=orgtype)
        download_url = (
            reverse("orgid_type_download", kwargs={"orgtype": orgtype})
            + "?"
            + request.GET.urlencode()
        )
    elif source:
        base_query = get_object_or_404(Source, id=source)
        s.set_criteria(source=source)
        download_url = (
            reverse("orgid_source_download", kwargs={"source": source})
            + "?"
            + request.GET.urlencode()
        )

    # add additional criteria from the get params
    s.set_criteria_from_request(request)

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

        def stream():
            buffer_ = Echo()
            writer = csv.writer(buffer_)
            yield writer.writerow(columns.values())
            s.run_db()
            res = s.query.values_list(*columns.keys()).order_by("org_id")
            prev_id = None
            for r in res:
                if r[0] != prev_id:
                    yield writer.writerow(r)
                prev_id = r[0]

        response = StreamingHttpResponse(stream(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="{}.csv"'.format(
            base_query.slug if base_query else "findthatcharity-search-results"
        )
        return response

    try:
        s.run_es(with_pagination=True, with_aggregation=True)
    except RequestError:
        if request.GET.get("q"):
            s.set_criteria(term='"' + request.GET["q"] + '"')
            s.run_es(with_pagination=True, with_aggregation=True)
        else:
            raise
    page_number = request.GET.get("page")
    page_obj = s.paginator.get_page(page_number)

    return render(
        request,
        "orgtype.html.j2",
        {
            "res": page_obj,
            "base_query": base_query,
            "download_url": download_url,
            "search": s,
        },
    )
