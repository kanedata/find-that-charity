import re
import datetime

from django.templatetags.static import static
from django.urls import reverse
from humanize import naturaldelta

from jinja2 import Environment


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


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'now': datetime.datetime.now(),
    })
    env.filters.update({
        'regex_search': regex_search,
        "naturaldelta": lambda x: naturaldelta(
            x, minimum_unit="milliseconds"),
    })
    return env
