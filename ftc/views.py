import csv
from collections import defaultdict

from charity_django.companies.models import Company
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_exempt
from django_sql_dashboard.models import Dashboard
from elasticsearch.exceptions import RequestError

from charity.models import Charity
from findthatcharity.utils import get_trending_organisations
from ftc.documents import OrganisationGroup
from ftc.models import Organisation, OrganisationType, RelatedOrganisation, Source
from ftc.query import (
    OrganisationSearch,
    get_linked_organisations,
    get_organisation,
    random_query,
)
from ftcprofile.controller import user_get_org_tags
from other_data.models import CQCProvider, Grant, WikiDataItem


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

    if request.user.is_anonymous:
        context["dashboards"] = [
            (dashboard, False)
            for dashboard in Dashboard.objects.filter(
                view_policy=Dashboard.ViewPolicies.PUBLIC
            )
            .select_related("owned_by", "view_group", "edit_group")
            .all()
        ]
    else:
        context["dashboards"] = [
            (dashboard, dashboard.user_can_edit(request.user))
            for dashboard in Dashboard.get_visible_to_user(request.user).select_related(
                "owned_by", "view_group", "edit_group"
            )
        ]

    context["trending_organisations"] = list(
        get_trending_organisations(context["examples"].values())
    )

    return render(request, "index.html.j2", context)


def about(request):
    context = {}
    return render(request, "about.html.j2", context)


@xframe_options_exempt
def get_org_by_id(request, org_id, filetype="html", preview=False, as_charity=False):
    org = get_organisation(org_id)
    charity = Charity.objects.filter(id=org_id).first()

    if filetype == "json":
        return JsonResponse(
            RelatedOrganisation([org]).to_json(
                as_charity,
                request=request,
                charity=charity,
            )
        )

    related_orgs = list(
        Organisation.objects.filter(linked_orgs__contains=[org_id]).select_related(
            "source"
        )
    )
    if not related_orgs:
        related_orgs = [org]
    related_orgs = RelatedOrganisation(related_orgs)

    additional_data = dict(
        cqc=CQCProvider.objects.filter(org_id__in=related_orgs.orgIDs).all(),
        grants_received=list(
            Grant.objects.filter(recipientOrganization_id__in=related_orgs.orgIDs)
            .order_by("-awardDate")
            .all()
        ),
        grants_given=list(
            Grant.objects.filter(fundingOrganization_id__in=related_orgs.orgIDs)
            .order_by("-awardDate")
            .all()
        ),
        wikidata=WikiDataItem.objects.filter(org_id__in=related_orgs.orgIDs).all(),
    )

    additional_data["grants_given_by_year"] = defaultdict(
        lambda: defaultdict(
            lambda: {
                "grants": 0,
                "amountAwarded": 0,
            }
        )
    )
    for g in additional_data["grants_given"]:
        additional_data["grants_given_by_year"][g.awardDate.year][g.currency][
            "grants"
        ] += 1
        additional_data["grants_given_by_year"][g.awardDate.year][g.currency][
            "amountAwarded"
        ] += g.amountAwarded

    template = "charity.html.j2" if charity else "org.html.j2"
    if preview:
        template = "org_preview.html.j2"

    return render(
        request,
        template,
        {
            "org": org,
            "related_orgs": related_orgs,
            "charity": charity,
            "tags": user_get_org_tags(request.user, org.org_id),
            **additional_data,
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
    q = OrganisationGroup.search().update_from_dict(
        random_query(active, "registered-charity")
    )[0]
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
            "linked_orgs": "linked_orgs",
            "linked_orgs_verified": "linked_orgs_verified",
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

    s.run_es(with_pagination=True, with_aggregation=True)
    page_number = request.GET.get("page")
    try:
        page_obj = s.paginator.get_page(page_number)
    except RequestError:
        return render(
            request,
            "error.html.j2",
            {
                "message": "Results not available, please try another search",
            },
            status=501,
        )

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


@xframe_options_exempt
def company_detail(request, company_number, filetype="html"):
    company = get_object_or_404(Company, CompanyNumber=company_number)

    # fetch any related organisations
    org = None
    orgs = list(
        Organisation.objects.filter(
            orgIDs__contains=["GB-COH-{}".format(company.CompanyNumber)]
        )
    )
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
            "source": Source.objects.get(id="companies"),
            "org": org,
        },
    )
