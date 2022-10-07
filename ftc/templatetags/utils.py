import json

from django import template
from django.utils.html import escape, urlize
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_type(value):
    return type(value).__name__


@register.filter
def format_cell_value(value):
    if isinstance(value, int):
        return "{:,.0f}".format(value)
    if isinstance(value, str) and value and value[0] in ("{", "["):
        try:
            return mark_safe(
                '<pre class="json">{}</pre>'.format(
                    escape(json.dumps(json.loads(value), indent=2))
                )
            )
        except json.JSONDecodeError:
            pass
    return mark_safe(urlize(value, nofollow=True, autoescape=True))
