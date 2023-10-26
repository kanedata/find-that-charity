from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    context = {}
    return render(request, "addtocsv/addtocsv.html.j2", context)
