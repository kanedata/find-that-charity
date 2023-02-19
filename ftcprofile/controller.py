from django.conf import settings
from django.db import IntegrityError

from ftc.query import get_organisation


def can_add_api_keys(user):
    api_keys = 0
    for key in user.apikey_set.all():
        if key.is_valid:
            api_keys += 1
        if api_keys >= settings.MAX_API_KEYS:
            return False
    return True


def user_has_starred_org(user, org_id):
    return user.tagged_organisations.filter(org_id=org_id).exists()


def user_has_tagged_org(user, org_id, tag):
    return user.tagged_organisations.filter(org_id=org_id, tag=tag).exists()


def user_tag_org(user, org_id, tag):
    try:
        user.tagged_organisations.create(org_id=org_id, tag=tag)
    except IntegrityError:
        pass


def user_untag_org(user, org_id, tag):
    user.tagged_organisations.filter(org_id=org_id, tag=tag).delete()


def user_get_org_tags(user, org_id):
    return user.tagged_organisations.filter(org_id=org_id).values_list("tag", flat=True)


def user_get_tagged_orgs(
    user,
):
    tagged_orgs = user.tagged_organisations.all()
    orgs = {}
    for org in tagged_orgs:
        if org.org_id not in orgs:
            orgs[org.org_id] = {
                "tags": [],
                "organisation": get_organisation(org.org_id),
            }
        orgs[org.org_id]["tags"].append(org.tag)
    for org in orgs.values():
        yield org["organisation"], org["tags"]
