from django.shortcuts import redirect

from charity.utils import regno_to_orgid
from ftc.views import get_org_by_id


def get_charity(request, regno, filetype="html", preview=False):
    org_id = regno_to_orgid(regno)

    if filetype == "html":
        return redirect("orgid_html", org_id=org_id, permanent=True)

    return get_org_by_id(request, org_id, filetype, preview, as_charity=True)
