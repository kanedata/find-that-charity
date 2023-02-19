from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django_sql_dashboard.models import Dashboard
from ninja_apikey.models import APIKey
from ninja_apikey.security import generate_key

from ftc.query import get_organisation
from ftcprofile.controller import (
    can_add_api_keys,
    user_get_org_tags,
    user_get_tagged_orgs,
    user_has_tagged_org,
    user_tag_org,
    user_untag_org,
)
from ftcprofile.forms import APIKeyForm


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
            "new_key_form": APIKeyForm() if can_add_api_keys(request.user) else None,
            "max_api_keys": settings.MAX_API_KEYS,
            "tagged_organisations": list(user_get_tagged_orgs(request.user)),
        },
    )


@login_required
def api_key_edit(request):
    context = {
        "message": None,
        "new_key_form": APIKeyForm(),
        "max_api_keys": settings.MAX_API_KEYS,
    }
    template = "partials/profile/apikeys.html.j2"

    def render_form(context):
        # if they've already for the max number of keys, don't let them add another
        if not can_add_api_keys(request.user):
            context["message"] = "You have reached the maximum number of API keys."
            context["new_key_form"] = None
            return render(request, template, context)
        return render(request, template, context)

    # show the new key form
    if request.method == "POST":
        revoke_key = request.POST.get("revoke_key")
        if revoke_key:
            key = APIKey.objects.get(prefix=revoke_key)
            key.revoked = True
            key.expires_at = timezone.now()
            key.save()
            context["message"] = f"API key {key.label} revoked"
            return render_form(context)

        new_key_form = APIKeyForm(request.POST)
        if new_key_form.is_valid():
            new_key = new_key_form.save(commit=False)
            new_key.user = request.user
            if not new_key.prefix:  # New API key
                key = generate_key()
                new_key.prefix = key.prefix
                new_key.hashed_key = key.hashed_key
            new_key.save()
            context["new_key"] = key
            context["message"] = (
                f"The API key for {new_key} is '{key.prefix}.{key.key}'. "
                "You should store it somewhere safe: "
                "you will not be able to see the key again."
            )
            return render_form(context)
        else:
            context["new_key_form"] = new_key_form
    return render_form(context)


@login_required
def tag_organisation(request, org_id):
    org = get_organisation(org_id)

    if request.method == "POST":
        tag = request.POST.get("tag")
        if not tag:
            raise ValueError("No tag provided")
        if user_has_tagged_org(request.user, org.org_id, tag):
            user_untag_org(request.user, org.org_id, tag)
        else:
            user_tag_org(request.user, org.org_id, tag)
    return render(
        request,
        "starred/status.html.j2",
        {
            "org": org,
            "tags": user_get_org_tags(request.user, org.org_id),
        },
    )
