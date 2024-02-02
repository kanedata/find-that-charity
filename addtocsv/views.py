from django.shortcuts import render
from django.urls import reverse


def index(request):
    context = {
        "properties_url": (
            request.build_absolute_uri(reverse("api-1.0:propose_properties"))
            + "?type=Organization"
        ),
        "extend_url": request.build_absolute_uri(reverse("api-1.0:reconcile_entities")),
        "orgid_schemes": {
            "orgid": ["Organisation Identifier", "GB-CHC-1234567"],
            "charity": ["Charity Number", "1234567"],
            "GB-CHC": ["Charity Number (England and Wales only)", "1234567"],
            "GB-SC": ["Charity Number (Scotland)", "SC012345"],
            "GB-NIC": ["Charity Number (Northern Ireland)", "123456"],
            "GB-COH": ["Company Number", "00123456"],
        },
    }
    return render(request, "addtocsv.html.j2", context)


def companies(request):
    context = {
        "properties_url": (
            request.build_absolute_uri(reverse("api-1.0:company_propose_properties"))
            + "?type=Company"
        ),
        "extend_url": request.build_absolute_uri(
            reverse("api-1.0:company_reconcile_entities")
        ),
        "orgid_schemes": {
            "GB-COH": ["Company Number", "00123456"],
        },
    }
    return render(request, "addtocsv.html.j2", context)
