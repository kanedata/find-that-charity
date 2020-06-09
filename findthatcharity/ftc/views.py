import csv

from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Q
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from ftc.documents import FullOrganisation
from ftc.models import (Organisation, OrganisationType, RelatedOrganisation,
                        Source)

# site homepage


# @cache_page(60 * 60)
def index(request):
    if 'q' in request.GET:
        return org_search(request)

    orgs = Organisation.objects

    by_orgtype = orgs.annotate(orgtype=Func(
        F('organisationType'), function='unnest')).values('orgtype').annotate(records=Count('*')).order_by('-records')
    by_source = orgs.values('source').annotate(
        records=Count('source')).order_by('-records')

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
    criteria = {}
    if 'q' in request.GET:
        criteria['name__search'] = request.GET['q']
    if 'orgtype' in request.GET and request.GET.get('orgtype') != 'all':
        criteria["organisationType__contains"] = [request.GET['orgtype']]

    orgs = Organisation.objects.filter(
        **{k: v for k, v in criteria.items() if v})
    paginator = Paginator(orgs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html.j2', {
        'res': page_obj,
        'term': request.GET.get('q'),
        'selected_org_type': request.GET.get('orgtype'),
    })


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


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    query = {
        'orgtype': [],
        'source': [],
        'q': None,
        'include_inactive': False,
    }
    if orgtype:
        query['base_query'] = get_object_or_404(OrganisationType, slug=orgtype)
        query['orgtype'].append(orgtype)
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
    if 'source' in request.GET:
        query['source'].extend(request.GET.getlist('source'))
    if 'q' in request.GET:
        query['q'] = request.GET['q']
    if request.GET.get('inactive') == 'include_inactive':
        query['include_inactive'] = True

    # convert query to criteria
    criteria = {}
    if query.get('orgtype'):
        criteria["organisationType__contains"] = query['orgtype']
    if query.get('source'):
        criteria["source__id__in"] = query['source']
    if query.get('q'):
        criteria['name__search'] = query['q']
    if not query.get('include_inactive') and filetype != 'csv':
        criteria['active'] = True

    orgs = Organisation.objects.filter(**{k: v for k, v in criteria.items() if v})

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
        res = orgs.values_list(*columns.keys()).order_by('org_id')
        for r in res:
            writer.writerow(r)
        return response
        

    by_orgtype = orgs.annotate(orgtype=Func(
        F('organisationType'), function='unnest')).values('orgtype').annotate(records=Count('*')).order_by('-records')
    by_source = orgs.values('source').annotate(records=Count('source')).order_by('-records')

    paginator = Paginator(orgs.order_by('name'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orgtype.html.j2', {
        "res": page_obj,
        "query": query,
        "term": request.GET.get('q'),
        "aggs": {
            "by_orgtype": by_orgtype,
            "by_source": by_source,
        },
        "download_url": download_url,
    })
