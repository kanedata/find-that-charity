import re

from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.http import JsonResponse

from ftc.models import Organisation, RelatedOrganisation

def get_charity(request, regno, filetype="html", preview=False):
    regno = regno.strip().upper()
    if regno.startswith("SC"):
        org_ids = ['GB-SC-{}'.format(regno)]
    elif regno.startswith("N"):
        org_ids = ['GB-NIC-{}'.format(re.sub('[^0-9]', '', regno))]
    else:
        org_ids = [
            'GB-CHC-{}'.format(regno),
            'GB-NIC-{}'.format(regno),
        ]
    for org_id in org_ids:
        orgs = list(Organisation.objects.filter(
            linked_orgs__contains=[org_id]))
        if orgs:
            break

    org = RelatedOrganisation(orgs)
    if filetype == "json":
        return JsonResponse({
            "org": org.to_json(charity=True)
        })
    return render(request, 'org.html.j2', {
        "org": org,
    })
