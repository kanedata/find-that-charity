import datetime

from django.core.cache import cache
from django.db import connection
from django.db.models import Count, F, Func
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from humanize import naturaldelta
from markdownx.utils import markdownify

from findthatcharity.utils import (
    a_or_an,
    format_currency,
    list_to_string,
    number_format,
    pluralise,
    regex_search,
    str_format,
    to_titlecase,
    url_remove,
    url_replace,
)
from ftc.models import Organisation, OrganisationType, OrgidScheme, Source
from geo.models import GeoLookup
from jinja2 import Environment


def get_orgtypes():
    cache_key = "orgtypes"
    value = cache.get(cache_key)
    if value:
        return value
    if OrganisationType._meta.db_table in connection.introspection.table_names():
        by_orgtype = {
            ot["orgtype"]: ot["records"]
            for ot in Organisation.objects.annotate(
                orgtype=Func(F("organisationType"), function="unnest")
            )
            .values("orgtype")
            .annotate(records=Count("*"))
            .order_by("-records")
        }
        value = {}
        for o in OrganisationType.objects.all():
            o.records = by_orgtype.get(o.slug, 0)
            value[o.slug] = o
        value = {
            k: v for k, v in sorted(value.items(), key=lambda item: -item[1].records)
        }
        cache.set(cache_key, value, 60 * 60)
    else:
        value = {}
    return value


def get_sources():
    cache_key = "sources"
    value = cache.get(cache_key)
    if value:
        return value
    if Source._meta.db_table in connection.introspection.table_names():
        value = {
            s.id: s
            for s in Source.objects.all()
            .annotate(records=Count("organisations"))
            .order_by("-records")
        }
        cache.set(cache_key, value, 60 * 60)
    else:
        value = {}
    return value


def get_orgidschemes():
    cache_key = "orgidschemes"
    value = cache.get(cache_key)
    if value:
        return value
    if OrgidScheme._meta.db_table in connection.introspection.table_names():
        value = {s.code: s for s in OrgidScheme.objects.all()}
        cache.set(cache_key, value, 60 * 60)
    else:
        value = {}
    return value


def get_locations():
    cache_key = "locationnames"
    value = cache.get(cache_key)
    if value:
        return value
    if GeoLookup._meta.db_table in connection.introspection.table_names():
        value = {}
        for s in GeoLookup.objects.all():
            if s.geoCodeType not in value:
                value[s.geoCodeType] = {}
            value[s.geoCodeType][s.geoCode] = s.name
        cache.set(cache_key, value, 60 * 60)
    else:
        value = {}
    return value


def get_geoname(code):
    try:
        return GeoLookup.objects.get(geoCode=code).name
    except GeoLookup.DoesNotExist:
        return code


def environment(**options):
    env = Environment(**options)

    env.globals.update(
        {
            "static": static,
            "url": reverse,
            "now": datetime.datetime.now(),
            "get_orgtypes": get_orgtypes,
            "get_sources": get_sources,
            "get_orgidschemes": get_orgidschemes,
            "get_locations": get_locations,
            "url_replace": url_replace,
            "url_remove": url_remove,
        }
    )
    env.filters.update(
        {
            "regex_search": regex_search,
            "naturaldelta": lambda x: naturaldelta(x, minimum_unit="milliseconds"),
            "list_to_string": list_to_string,
            "slugify": slugify,
            "titlecase": to_titlecase,
            "pluralise": pluralise,
            "get_geoname": get_geoname,
            "format_currency": format_currency,
            "str_format": str_format,
            "a_or_an": a_or_an,
            "markdown": markdownify,
            "number_format": number_format,
        }
    )
    return env
