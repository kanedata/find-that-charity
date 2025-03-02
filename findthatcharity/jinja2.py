import datetime
import os

from charity_django.utils.text import list_to_string, regex_search, to_titlecase
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.core.cache import cache
from django.db import connections
from django.db.models import Count, F, Func
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from markdownx.utils import markdownify

from findthatcharity.utils import (
    a_or_an,
    format_currency,
    number_format,
    pluralise,
    process_wikipedia_url,
    str_format,
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
    if (
        OrganisationType._meta.db_table
        in connections["data"].introspection.table_names()
    ):
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


def orgtypes_to_dict(orgtypes):
    return {o.slug: o.title for o in orgtypes.values()}


def get_sources(split=False):
    cache_key = "sources"
    value = cache.get(cache_key)
    if not value:
        if Source._meta.db_table in connections["data"].introspection.table_names():
            value = {
                s.id: s
                for s in Source.objects.all()
                .annotate(records=Count("organisations"))
                .order_by("-records")
            }
            cache.set(cache_key, value, 60 * 60)
        else:
            value = {}

    if split:
        MONTH_AGO = datetime.datetime.now() - datetime.timedelta(days=30)
        return {
            "current": {
                k: v
                for k, v in value.items()
                if v.modified is None or (v.modified > MONTH_AGO)
            },
            "archive": {
                k: v
                for k, v in value.items()
                if v.modified is not None and (v.modified <= MONTH_AGO)
            },
        }

    return value


def get_orgidschemes():
    cache_key = "orgidschemes"
    value = cache.get(cache_key)
    if value:
        return value
    if OrgidScheme._meta.db_table in connections["data"].introspection.table_names():
        value = {s.code: s for s in OrgidScheme.objects.all()}
        cache.set(cache_key, value, 60 * 60)
    else:
        value = {}
    return value


def get_locations(areatypes=settings.DEFAULT_AREA_TYPES):
    cache_key = "locationnames"
    value = cache.get(cache_key)
    if value:
        return value
    if GeoLookup._meta.db_table in connections["data"].introspection.table_names():
        value = {}
        for s in GeoLookup.objects.filter(geoCodeType__in=areatypes):
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
            "debug": settings.DEBUG,
            "GIT_REV": os.environ.get("GIT_REV"),
        }
    )
    env.filters.update(
        {
            "regex_search": regex_search,
            "naturalday": naturalday,
            "naturaltime": naturaltime,
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
            "orgtypes_to_dict": orgtypes_to_dict,
            "process_wikipedia_url": process_wikipedia_url,
        }
    )
    return env
