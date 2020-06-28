import csv

from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from ftc.documents import FullOrganisation, DSEPaginator
from ftc.models import (Organisation, OrganisationType, RelatedOrganisation,
                        Source)
from ftc.query import random_query, OrganisationSearch
from reconcile.query import recon_query

# site homepage
@cache_page(60 * 60)
def index(request):
    if 'q' in request.GET:
        return org_search(request)

    orgs = Organisation.objects

    by_orgtype = orgs.annotate(
        orgtype=Func(
            F('organisationType'),
            function='unnest')
        ).values('orgtype').annotate(
            records=Count('*')
        ).order_by('-records')
    by_source = Source.objects.all().annotate(
        records=Count('organisations')
    ).order_by('-records')

    context = dict(
        examples = {
            'registered-charity-england-and-wales': 'GB-CHC-1177548',
            'registered-charity-scotland': 'GB-SC-SC007427',
            'registered-charity-northern-ireland': 'GB-NIC-104226',
            'community-interest-company': 'GB-COH-08255580',
            'local-authority': 'GB-LAE-IPS',
            'universities': 'GB-EDU-133808',
        },
        term='',
        by_orgtype=by_orgtype,
        by_source=by_source,
    )
    return render(request, 'index.html.j2', context)


def org_search(request):

    s = OrganisationSearch()
    if 'q' in request.GET:
        s.set_criteria(term=request.GET['q'])
    if 'orgtype' in request.GET and request.GET.get('orgtype') != 'all':
        s.set_criteria(base_orgtype=request.GET.get('orgtype'))
        
    s.run_es(with_pagination=True, with_aggregation=False)
    page_number = request.GET.get('page')
    page_obj = s.paginator.get_page(page_number)

    return render(request, 'search.html.j2', {
        'res': page_obj,
        'term': request.GET.get('q'),
        'selected_org_type': request.GET.get('orgtype'),
    })


def search_organisations(criteria, use_pagination=True, search_source='elasticsearch'):
    if search_source not in ('elasticsearch', 'db'):
        raise ValueError("Search source must be elasticsearch or db")

    if search_source == 'elasticsearch':
        query_template, params = recon_query(
            query,
            orgtype=orgtype,
        )
        q = FullOrganisation.search().from_dict(query_template)
        result = q.execute(params=params)
        paginator = DSEPaginator(result, 25)

def get_orgid(request, org_id, filetype="html", preview=False):
    orgs = get_list_or_404(Organisation, linked_orgs__contains=[org_id])
    org = RelatedOrganisation(orgs)
    if filetype=="json":
        return JsonResponse({
            "org": org.to_json()
        })
    return render(request, 'org.html.j2', {
        "org": org,
    })


def get_random_org(request):
    """ Get a random charity record
    """
    filetype = request.GET.get("filetype", "html")
    active = request.GET.get("active", False)
    q = FullOrganisation.search().from_dict(random_query(active, "registered-charity"))[0]
    result = q.execute()
    for r in result:
        return JsonResponse(r.__dict__['_d_'])


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    query = {
        'orgtype': [],
        'source': [],
        'q': None,
        'include_inactive': False,
    }
    s = OrganisationSearch()
    if orgtype:
        query['base_query'] = get_object_or_404(OrganisationType, slug=orgtype)
        query['orgtype'].append(orgtype)
        s.set_criteria(base_orgtype=orgtype)
        download_url = reverse('orgid_type_download', 
                                kwargs={'orgtype': orgtype})
    elif source:
        query['base_query'] = get_object_or_404(Source, id=source)
        query['source'].append(source)
        download_url = reverse('orgid_source_download',
                               kwargs={'source': source})
    if request.GET:
        download_url += '?' + request.GET.urlencode()

    # add additional criteria from the get params
    if 'orgtype' in request.GET:
        query['orgtype'].extend(
            request.GET.getlist('orgtype'))
        s.set_criteria(other_orgtypes=request.GET.getlist('orgtype'))
    if 'source' in request.GET:
        query['source'].extend(request.GET.getlist('source'))
    if 'q' in request.GET:
        query['q'] = request.GET['q']
        s.set_criteria(term=query['q'])
    if request.GET.get('inactive') == 'include_inactive':
        query['include_inactive'] = True

    # convert query to criteria
    s.set_criteria(source=query['source'])
    if not query.get('include_inactive') and filetype != 'csv':
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
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(
            query['base_query'].slug
        )
        writer = csv.writer(response)
        writer.writerow(columns.values())
        s.run_db()
        res = s.query.values_list(*columns.keys()).order_by('org_id')
        for r in res:
            writer.writerow(r)
        return response

    s.run_es(with_pagination=True, with_aggregation=True)
    page_number = request.GET.get('page')
    page_obj = s.paginator.get_page(page_number)
    print(page_obj.has_other_pages())

    return render(request, 'orgtype.html.j2', {
        "res": page_obj,
        "query": query,
        "term": request.GET.get('q'),
        "aggs": {
            "by_orgtype": s.aggregation.get("by_orgtype"),
            "by_source": s.aggregation.get("by_source"),
        },
        "download_url": download_url,
    })
