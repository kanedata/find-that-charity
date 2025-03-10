from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.urls import resolve, reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django_better_admin_arrayfield.admin.mixins import DynamicArrayMixin
from prettyjson.widgets import PrettyJSONWidget

from ftc import models as ftc


class MyPrettyJSONWidget(PrettyJSONWidget):
    def render(self, name, value, attrs=None, **kwargs):
        html = super(MyPrettyJSONWidget, self).render(name, value, attrs)
        return mark_safe(html)


class JSONFieldAdmin(admin.ModelAdmin, DynamicArrayMixin):
    list_per_page = 20
    formfield_overrides = {
        models.JSONField: {"widget": MyPrettyJSONWidget({"initial": "parsed"})}
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
    list_display = (
        "id",
        "publisher",
        "title",
        "organisation_count",
        "organisation_link_count",
        "organisation_location_count",
    )
    search_fields = ("title",)
    list_filter = ()
    formfield_overrides = {
        "data": {"widget": Textarea(attrs={"rows": "15", "cols": "35"})},
    }

    def organisation_count(self, obj):
        return obj.organisations.count()

    def organisation_link_count(self, obj):
        return obj.organisation_links.count()

    def organisation_location_count(self, obj):
        return obj.organisation_locations.count()


class ScrapeAdmin(SourceAdmin):
    list_display = (
        "id",
        "spider",
        "start_time",
        "finish_time",
        "status",
        "errors",
        "items",
        "organisation_count",
        "organisation_link_count",
        "organisation_location_count",
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
    formfield_overrides = {
        models.JSONField: {"widget": MyPrettyJSONWidget({"initial": "parsed"})},
    }

    class Media:
        css = {"all": ("css/admin/scrape.css",)}


class VocabularyEntriesInline(admin.TabularInline):
    model = ftc.VocabularyEntries
    extra = 1

    def get_parent_object_from_request(self, request):
        """
        Returns the parent object from the request or None.

        Note that this only works for Inlines, because the `parent_model`
        is not available in the regular admin.ModelAdmin as an attribute.
        """
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        if resolved.kwargs:
            return self.parent_model.objects.get(pk=resolved.kwargs.get("object_id"))
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            vocab = self.get_parent_object_from_request(request)
            kwargs["queryset"] = ftc.VocabularyEntries.objects.filter(vocabulary=vocab)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VocabularyAdmin(JSONFieldAdmin):
    list_display = ("title", "entries")
    # inlines = [VocabularyEntriesInline]

    def entries(self, obj):
        return obj.entries.count()


class VocabularyEntriesAdmin(JSONFieldAdmin):
    list_display = (
        "code_",
        "vocabulary",
        "title",
        "parent",
    )

    def code_(self, obj):
        if slugify(obj.title) == slugify(obj.code):
            return obj.id
        return obj.code


class PersonalDataAdmin(admin.ModelAdmin):
    list_display = ("org_id", "notes")


admin.site.site_header = "Find that Charity admin"
admin.site_site_title = admin.site.site_header

admin.site.register(ftc.Organisation, OrganisationAdmin)
admin.site.register(ftc.OrganisationType, JSONFieldAdmin)
admin.site.register(ftc.OrganisationLink, JSONFieldAdmin)
admin.site.register(ftc.Source, SourceAdmin)
admin.site.register(ftc.Scrape, ScrapeAdmin)
admin.site.register(ftc.OrgidScheme, JSONFieldAdmin)
admin.site.register(ftc.Vocabulary, VocabularyAdmin)
admin.site.register(ftc.VocabularyEntries, VocabularyEntriesAdmin)
admin.site.register(ftc.PersonalData, PersonalDataAdmin)
