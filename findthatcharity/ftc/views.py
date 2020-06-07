from django.forms.models import model_to_dict
from django.db.models import Q, Count, Func, F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.core.paginator import Paginator

from ftc.documents import FullOrganisation
from ftc.models import Organisation, RelatedOrganisation

# site homepage
def index(request):
    context = {}
    return render(request, 'index.html.j2', context)


def get_orgid(request, org_id, filetype="html"):
    orgs = get_list_or_404(Organisation, linked_orgs__contains=[org_id])
    org = RelatedOrganisation(orgs)
    if filetype=="json":
        return JsonResponse({
            "org": org.to_json()
        })
    return render(request, 'org.html.j2', {
        "org": org,
    })


def get_orgid_by_hash(request, org_id, filetype="html"):
    return HttpResponse()


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    criteria = {
        "organisationType__contains": [],
        "source__id__in": [],
    }
    if orgtype:
        criteria["organisationType__contains"].append(orgtype)
    if source:
        criteria["source__id__in"].append(source)

    if 'orgtype' in request.GET:
        criteria["organisationType__contains"].extend(
            request.GET.getlist('orgtype'))

    if 'source' in request.GET:
        criteria["source__id__in"].extend(request.GET.getlist('source'))

    if 'q' in request.GET:
        criteria['name__search'] = request.GET['q']
    print(criteria)

    orgs = Organisation.objects.filter(**{k: v for k, v in criteria.items() if v})




    by_orgtype = orgs.annotate(orgtype=Func(
        F('organisationType'), function='unnest')).values('orgtype').annotate(records=Count('*')).order_by('-records')
    by_source = orgs.values('source').annotate(records=Count('source')).order_by('-records')

    paginator = Paginator(orgs.order_by('name'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orgtype.html.j2', {
        "res": page_obj,
        "query": criteria,
        "term": request.GET.get('q'),
        "aggs": {
            "by_orgtype": by_orgtype,
            "by_source": by_source,
        }
    })



def orgid_type_download(request, orgtype=None, source=None, filetype="html"):
    return HttpResponse()
