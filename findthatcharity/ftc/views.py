from django.forms.models import model_to_dict
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_list_or_404, get_object_or_404

from ftc.documents import FullOrganisation
from ftc.models import Organisation

# site homepage
def index(request):
    context = {}
    return render(request, 'index.html.j2', context)


def get_orgid(request, org_id, filetype="html"):
    orgs = get_list_or_404(Organisation, linked_orgs__contains=[org_id])
    orgs = Organisation.prioritise_orgs(orgs)
    org = orgs[0]
    if filetype=="json":
        return JsonResponse({
            "org": org.to_json()
        })
    return render(request, 'org.html.j2', {
        "org": org,
        "orgs": orgs,
    })


def get_orgid_by_hash(request, org_id, filetype="html"):
    return HttpResponse()


def orgid_type(request, orgtype=None, source=None, filetype="html"):
    print(orgtype)
    print(source)
    return HttpResponse()


def orgid_type_download(request, orgtype=None, source=None, filetype="html"):
    return HttpResponse()
