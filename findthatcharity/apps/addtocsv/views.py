from django.shortcuts import render


def index(request):
    context = {}
    return render(request, "addtocsv/addtocsv.html.j2", context)
