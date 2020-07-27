from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from prettyjson.widgets import PrettyJSONWidget

from ftc import models as ftc


class JSONFieldAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_per_page = 20
    formfield_overrides = {
        JSONField: {"widget": PrettyJSONWidget(attrs={"initial": "parsed"})}
    }


# class CharityFinancialInline(admin.TabularInline):
#     model = charity.CharityFinancial
#     extra = 1


# class CharityNameInline(admin.TabularInline):
#     model = charity.CharityName
#     extra = 1


class OrganisationAdmin(JSONFieldAdmin):
    list_display = (
        "org_id",
        "name",
        "source_",
        "scrape_",
        "organisation_type",
        "active",
        "dateRegistered",
        "dateRemoved",
    )
    list_filter = ("active", "source", "organisationTypePrimary")
    search_fields = ["name"]

    def source_(self, obj):
        link = reverse("admin:ftc_source_change", args=[obj.source.id])
        return mark_safe('<a href="%s">%s</a>' % (link, str(obj.source)))

    def scrape_(self, obj):
        link = reverse("admin:ftc_scrape_change", args=[obj.scrape.id])
        return mark_safe('<a href="%s">%s</a>' % (link, str(obj.scrape)))

    def organisation_type(self, obj):
        link = reverse(
            "admin:ftc_organisationtype_change", args=[obj.organisationTypePrimary.slug]
        )
        return mark_safe(
            '<a href="%s">%s</a>' % (link, str(obj.organisationTypePrimary))
        )

    # inlines = [CharityFinancialInline, CharityNameInline]

    # def view_on_site(self, obj):
    #     url = reverse('charity_html', kwargs={'regno': obj.id.replace(
    #         'GB-CHC-', '').replace('GB-SC-', '').replace('GB-NIC-', '')})
    #     return url


class SourceAdmin(JSONFieldAdmin):
    list_display = ("id", "publisher", "title", "item_count", "link_count")
    search_fields = ("title",)
    list_filter = ()

    def item_count(self, obj):
        return obj.organisations.count()

    def link_count(self, obj):
        return obj.organisation_links.count()


class ScrapeAdmin(SourceAdmin):
    list_display = (
        "id",
        "spider",
        "start_time",
        "finish_time",
        "status",
        "errors",
        "items",
        "item_count",
        "link_count",
    )
    list_filter = (
        "status",
        "spider",
    )
    search_fields = ()
    readonly_fields = [
        "start_time",
        "finish_time",
        "log",
        "result",
        "items",
        "errors",
        "status",
    ]

    class Media:
        css = {"all": ("css/admin/scrape.css",)}


admin.site.site_header = "Find that Charity admin"
admin.site_site_title = admin.site.site_header

admin.site.register(ftc.Organisation, OrganisationAdmin)
admin.site.register(ftc.OrganisationType, JSONFieldAdmin)
admin.site.register(ftc.OrganisationLink, JSONFieldAdmin)
admin.site.register(ftc.Source, SourceAdmin)
admin.site.register(ftc.Scrape, ScrapeAdmin)
admin.site.register(ftc.OrgidScheme, JSONFieldAdmin)
