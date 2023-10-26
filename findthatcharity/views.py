from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def missing_page_handler(request: HttpRequest, exception=None) -> HttpResponse:
    return render(
        request,
        "error.html.j2",
        {
            "message": str(exception) if exception else "Page not found",
        },
        status=404,
    )
