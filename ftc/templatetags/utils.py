import json

from django import template
from django.utils.html import escape, format_html_join, urlize
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


@register.filter(name="group_tables")
def group_tables(value):
    """Split an array of tables into groups based on the table prefix"""
    tables = {}
    for table in value:
        prefix = table["name"].split("_")[0]
        if prefix not in tables:
            tables[prefix] = []
        tables[prefix].append(table)
    for prefix, tables in tables.items():
        yield prefix, tables


@register.filter(name="list_to_tags")
def list_to_tags(value):
    """Convert a list of strings into a list of tags"""
    return format_html_join(
        "\n",
        '<span class="code bg-light-gray ph1 pv0 br2 mr2 mb2 f6 dib">{}</span>',
        ((tag.strip(),) for tag in value.split(",")),
    )
