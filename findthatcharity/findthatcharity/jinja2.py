import datetime
import re

from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from django.db import connection
from humanize import naturaldelta
from jinja2 import Environment

from ftc.models import OrganisationType, Source


def regex_search(s, regex):
    return re.search(regex, s) is not None


def list_to_string(l, sep=", ", final_sep=" and "):
    if not isinstance(l, list):
        return l

    if len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return final_sep.join(l)
    else:
        return sep.join(l[0:-1]) + final_sep + l[-1]


def url_replace(request, **kwargs):
    dict_ = request.GET.copy()
    for field, value in kwargs.items():
        dict_[field] = value
    return request.build_absolute_uri(request.path) + '?' + dict_.urlencode()

def url_remove(request, fields):
    dict_ = request.GET.copy()
    if not isinstance(fields, list):
        fields = [fields]
    for field in fields:
        if field in dict_:
            del dict_[field]
    return request.build_absolute_uri(request.path) + '?' + dict_.urlencode()

def environment(**options):
    env = Environment(**options)

    orgtypes = {}
    sources = {}
    if OrganisationType._meta.db_table in connection.introspection.table_names():
        orgtypes = {o.slug: o for o in OrganisationType.objects.all()}
    if Source._meta.db_table in connection.introspection.table_names():
        sources = {s.id: s for s in Source.objects.all()}

    env.globals.update({
        'static': static,
        'url': reverse,
        'now': datetime.datetime.now(),
        'orgtypes': orgtypes,
        'sources': sources,
        "url_replace": url_replace,
        "url_remove": url_remove,
    })
    env.filters.update({
        'regex_search': regex_search,
        "naturaldelta": lambda x: naturaldelta(
            x, minimum_unit="milliseconds"),
        "list_to_string": list_to_string,
        "slugify": slugify,
    })
    return env
