import re
from decimal import Decimal
from urllib.parse import urlparse

import babel.numbers
import inflect
from django.conf import settings
from django.http import HttpRequest

WORD_BOUNDARY_REGEX = re.compile(r"\b\w+\b")

p = inflect.engine()


def url_replace(request: HttpRequest, **kwargs) -> str:
    dict_ = request.GET.copy()
    for field, value in kwargs.items():
        dict_[field] = value
    return request.build_absolute_uri(request.path) + "?" + dict_.urlencode()


def url_remove(request: HttpRequest, fields: list[str] | str) -> str:
    dict_ = request.GET.copy()
    if not isinstance(fields, list):
        fields = [fields]
    for field in fields:
        if field in dict_:
            del dict_[field]
    return request.build_absolute_uri(request.path) + "?" + dict_.urlencode()


def pluralise(
    text: str,
    count: int = 1,
    number_format: str = ":,.0f",
    text_format="{count} {text}",
) -> str:
    count_str = ("{" + number_format + "}").format(count)
    return text_format.format(count=count_str, text=p.plural(text, count))


def format_currency(
    amount: float | int | Decimal, currency: str = "GBP", int_format: str = "¤#,##0"
) -> str:
    return babel.numbers.format_currency(
        amount, currency, format=int_format, currency_digits=False, locale="en_UK"
    )


def number_format(value: float | int | Decimal, scale=1, negative=False) -> str:
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
    return format_.format(float(value) / float(scale))


def str_format(value: float | int | Decimal, format: str = "{}") -> str:
    return format.format(value)


def a_or_an(value: str) -> str:
    return p.a(value).split()[0]


def normalise_name(n: str) -> str:
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


def get_domain(url: str) -> str | None:
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
