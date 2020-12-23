import re

from django.http import Http404

from ftc.views import get_org_by_id


def get_charity(request, regno, filetype="html", preview=False):
    regno = regno.strip().upper()
    if regno.startswith("SC"):
        org_ids = ["GB-SC-{}".format(regno)]
    elif regno.startswith("N"):
        org_ids = ["GB-NIC-{}".format(re.sub("[^0-9]", "", regno))]
    else:
        org_ids = [
            "GB-CHC-{}".format(regno),
            "GB-NIC-{}".format(regno),
        ]
    for org_id in org_ids:
        try:
            return get_org_by_id(request, org_id, filetype, preview, as_charity=True)
        except Http404:
            continue
    raise Http404("Charity not found")
