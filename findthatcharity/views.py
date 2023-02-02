from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django_sql_dashboard.models import Dashboard


def missing_page_handler(request, exception=None):
    return render(
        request,
        "error.html.j2",
        {
            "message": str(exception) if exception else "Page not found",
        },
        status=404,
    )


@login_required
def account_profile(request):
    return render(
        request,
        "account_profile.html.j2",
        {
            "dashboards": {
                "visible": Dashboard.get_visible_to_user(request.user).order_by("slug"),
                "editable": Dashboard.get_editable_by_user(request.user).order_by(
                    "slug"
                ),
            },
        },
    )
