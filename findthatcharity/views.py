from django.shortcuts import render


def missing_page_handler(request, exception=None):
    return render(
        request,
        "error.html.j2",
        {
            "message": str(exception) if exception else "Page not found",
        },
        status=404,
    )
