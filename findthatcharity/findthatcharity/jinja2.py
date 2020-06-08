import datetime
import re

from django.templatetags.static import static
from django.urls import reverse
from humanize import naturaldelta
from jinja2 import Environment

from ftc.models import OrganisationType, Source


def regex_search(s, regex):
    return re.search(regex, s) is not None


# templates = Jinja2Templates(directory='templates')

# templates.env.filters["list_to_string"] = list_to_string
# templates.env.filters["regex_search"] = regex_search
# templates.env.filters["slugify"] = slugify
# templates.env.filters["naturaldelta"] = 
# templates.env.globals["sources"] = fetch_all_sources()
# templates.env.globals["org_types"] = ORGTYPES
# templates.env.globals["sources_count"] = SOURCES
# templates.env.globals["key_types"] = settings.KEY_TYPES
# templates.env.globals["now"] = datetime.datetime.now()


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
    env.globals.update({
        'static': static,
        'url': reverse,
        'now': datetime.datetime.now(),
        'orgtypes': {o.slug: o for o in OrganisationType.objects.all()},
        'sources': {s.id: s for s in Source.objects.all()},
        "url_replace": url_replace,
        "url_remove": url_remove,
    })
    env.filters.update({
        'regex_search': regex_search,
        "naturaldelta": lambda x: naturaldelta(
            x, minimum_unit="milliseconds"),
    })
    return env
