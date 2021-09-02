import re

from django.shortcuts import redirect

from ftc.views import get_org_by_id


def get_charity(request, regno, filetype="html", preview=False):
    regno = regno.strip().upper()
    if regno.startswith("SC"):
        org_id = "GB-SC-{}".format(regno)
    elif regno.startswith("N") or (regno.startswith("1") and len(regno) == 6):
        org_id = "GB-NIC-{}".format(re.sub("[^0-9]", "", regno))
    else:
        org_id = "GB-CHC-{}".format(regno)

    if filetype == "html":
        return redirect("orgid_html", org_id=org_id, permanent=True)

    return get_org_by_id(request, org_id, filetype, preview, as_charity=True)
