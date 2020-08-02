import datetime

from django.db import connection
from django.db.models import Count
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from humanize import naturaldelta

from findthatcharity.utils import (list_to_string, regex_search, to_titlecase,
                                   url_remove, url_replace, pluralise)
from ftc.models import OrganisationType, Source, OrgidScheme
from jinja2 import Environment


def environment(**options):
    env = Environment(**options)

    orgtypes = {}
    sources = {}
    if OrganisationType._meta.db_table in connection.introspection.table_names():
        orgtypes = {o.slug: o for o in OrganisationType.objects.all()}
    if Source._meta.db_table in connection.introspection.table_names():
        sources = {
            s.id: s
            for s in Source.objects.all()
            .annotate(records=Count("organisations"))
            .order_by("-records")
        }
    if OrgidScheme._meta.db_table in connection.introspection.table_names():
        orgidschemes = {s.code: s for s in OrgidScheme.objects.all()}

    env.globals.update({
        'static': static,
        'url': reverse,
        'now': datetime.datetime.now(),
        'orgtypes': orgtypes,
        'sources': sources,
        'orgidschemes': orgidschemes,
        "url_replace": url_replace,
        "url_remove": url_remove,
    })
    env.filters.update({
        'regex_search': regex_search,
        "naturaldelta": lambda x: naturaldelta(
            x, minimum_unit="milliseconds"),
        "list_to_string": list_to_string,
        "slugify": slugify,
        "titlecase": to_titlecase,
        "pluralise": pluralise,
    })
    return env
