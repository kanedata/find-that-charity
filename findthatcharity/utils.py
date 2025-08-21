import re
from urllib.parse import urlparse

import babel.numbers
import inflect
import requests
from django.conf import settings
from django.core.cache import cache

from ftc.models.organisation import Organisation

WORD_BOUNDARY_REGEX = re.compile(r"\b\w+\b")

p = inflect.engine()


def url_replace(request, **kwargs):
    dict_ = request.GET.copy()
    for field, value in kwargs.items():
        dict_[field] = value
    return request.build_absolute_uri(request.path) + "?" + dict_.urlencode()


def url_remove(request, fields):
    dict_ = request.GET.copy()
    if not isinstance(fields, list):
        fields = [fields]
    for field in fields:
        if field in dict_:
            del dict_[field]
    return request.build_absolute_uri(request.path) + "?" + dict_.urlencode()


def pluralise(text, count=1, number_format=":,.0f", text_format="{count} {text}"):
    count_str = ("{" + number_format + "}").format(count)
    return text_format.format(count=count_str, text=p.plural(text, count))


def format_currency(amount, currency="GBP", int_format="¤#,##0"):
    return babel.numbers.format_currency(
        amount, currency, format=int_format, currency_digits=False, locale="en_UK"
    )


def number_format(value, scale=1, negative=False):
    if value is None or value == 0:
        return "-"
    format_ = "{:,.0f}"
    if scale > 1:
        format_ = "{:,.1f}"
    if negative:
        value = -value
    if value < 0:
        format_ = "(" + format_ + ")"
        value = abs(value)
    return format_.format(value / float(scale))


def str_format(value, format="{}"):
    return format.format(value)


def a_or_an(value):
    return p.a(value).split()[0]


def normalise_name(n):
    stopwords = [
        "the",
        "of",
        "in",
        "uk",
        "ltd",
        "limited",
        "and",
        "&",
        "+",
        "co",
        "for",
    ]
    return " ".join(
        [w for w in WORD_BOUNDARY_REGEX.findall(n.lower()) if w not in stopwords]
    ).strip()


def get_domain(url):
    if not url:
        return None
    if not url.startswith("http"):
        url = "http://" + url
    try:
        domain = urlparse(url).netloc
    except ValueError:
        return None
    if domain.startswith("www."):
        domain = domain[4:]
    if domain in settings.IGNORE_DOMAINS:
        return None
    return domain


def get_trending_organisations(examples):
    def get_from_simple_analytics():
        if settings.SIMPLE_ANALYTICS_API_KEY:
            try:
                r = requests.get(
                    "https://simpleanalytics.com/findthatcharity.uk.json?fields=pages&version=5&pages=%2Forgid%2FGB-*",
                    headers={
                        "Api-Key": settings.SIMPLE_ANALYTICS_API_KEY,
                    },
                )
                r.raise_for_status()
                organisations = [
                    {
                        **page,
                        "org_id": page["value"].split("/")[-1],
                    }
                    for page in r.json()["pages"]
                ]
                for org in organisations:
                    if org["org_id"] in examples:
                        continue
                    organisation = Organisation.objects.filter(
                        org_id=org["org_id"]
                    ).first()
                    if not organisation:
                        continue
                    if org["pageviews"] < 10:
                        continue
                    yield {
                        **org,
                        "organisation": organisation,
                    }
            except Exception as e:
                print(e.msg)
                pass
        return []

    return cache.get_or_set(
        "trending_organisations",
        lambda: list(get_from_simple_analytics()),
        60 * 60 * 24,
    )


def process_wikipedia_url(url):
    end_part = url.split("/")[-1]
    return end_part.replace("_", " ")


def can_view_postcode(request):
    if (
        request
        and settings.FTC_SHOW_POSTCODE
        and (request.headers.get("FTC-SHOW-POSTCODE") == settings.FTC_SHOW_POSTCODE)
    ):
        return True
    return False
