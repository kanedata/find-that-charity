import re
from urllib.parse import urlparse

import babel.numbers
import inflect
import titlecase
from django.conf import settings
from django.utils.text import slugify

VOWELS = re.compile("[AEIOUYaeiouy]")
ORD_NUMBERS_RE = re.compile(r"([0-9]+(?:st|nd|rd|th))")
SENTENCE_SPLIT = re.compile(r"(\. )")

p = inflect.engine()


def title_exceptions(word, **kwargs):

    word_test = word.strip("(){}<>.")

    # lowercase words
    if word_test.lower() in ["a", "an", "of", "the", "is", "or"]:
        return word.lower()

    # uppercase words
    if word_test.upper() in [
        "UK",
        "FM",
        "YMCA",
        "PTA",
        "PTFA",
        "NHS",
        "CIO",
        "U3A",
        "RAF",
        "PFA",
        "ADHD",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "AFC",
        "CE",
        "CIC",
    ]:
        return word.upper()

    # words with no vowels that aren't all uppercase
    if word_test.lower() in [
        "st",
        "mr",
        "mrs",
        "ms",
        "ltd",
        "dr",
        "cwm",
        "clwb",
        "drs",
    ]:
        return word_test.title()

    # words with number ordinals
    if bool(ORD_NUMBERS_RE.search(word_test.lower())):
        return word.lower()

    # words with dots/etc in the middle
    for s in [".", "'", ")"]:
        dots = word.split(s)
        if len(dots) > 1:
            # check for possesive apostrophes
            if s == "'" and dots[-1].upper() == "S":
                return s.join(
                    [
                        titlecase.titlecase(i, callback=title_exceptions)
                        for i in dots[:-1]
                    ]
                    + [dots[-1].lower()]
                )
            # check for you're and other contractions
            if word_test.upper() in ["YOU'RE", "DON'T", "HAVEN'T"]:
                return s.join(
                    [
                        titlecase.titlecase(i, callback=title_exceptions)
                        for i in dots[:-1]
                    ]
                    + [dots[-1].lower()]
                )
            return s.join(
                [titlecase.titlecase(i, callback=title_exceptions) for i in dots]
            )

    # words with no vowels in (treat as acronyms)
    if not bool(VOWELS.search(word_test)):
        return word.upper()

    return None


def to_titlecase(s, sentence=False):
    if type(s) != str:
        return s

    s = s.strip()

    # if it contains any lowercase letters then return as is
    if not s.isupper() and not s.islower():
        return s

    # if it's a sentence then use capitalize
    if sentence:
        return "".join([sent.capitalize() for sent in re.split(SENTENCE_SPLIT, s)])

    # try titlecasing
    s = titlecase.titlecase(s, callback=title_exceptions)

    # Make sure first letter is capitalise
    return s[0].upper() + s[1:]


def regex_search(s, regex):
    return re.search(regex, s) is not None


def list_to_string(items, sep=", ", final_sep=" and "):
    if isinstance(items, str):
        return items
    if isinstance(items, set):
        items = list(items)

    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return final_sep.join(items)
    else:
        return sep.join(items[0:-1]) + final_sep + items[-1]


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
    stopwords = ["the", "of", "in", "uk", "ltd", "limited"]
    n = slugify(n)
    return " ".join([w for w in n.split("-") if w not in stopwords])


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
