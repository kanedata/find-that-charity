from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from findthatcharity.apps.charity.utils import regno_to_orgid
from findthatcharity.apps.ftc.views import get_org_by_id


def get_charity(
    request: HttpRequest, regno: str, filetype: str = "html", preview: bool = False
) -> HttpResponse:
    org_id = regno_to_orgid(regno)

    if filetype == "html":
        return redirect("orgid_html", org_id=org_id, permanent=True)

    return get_org_by_id(request, org_id, filetype, preview, as_charity=True)
