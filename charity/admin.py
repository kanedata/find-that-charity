from django.contrib import admin
from django.db import models
from django.urls import resolve, reverse
from django.utils.text import slugify
from prettyjson.widgets import PrettyJSONWidget

from charity import models as charity


class JSONFieldAdmin(admin.ModelAdmin):
    list_per_page = 20
    formfield_overrides = {
        models.JSONField: {"widget": PrettyJSONWidget(attrs={"initial": "parsed"})}
    }


class CharityFinancialInline(admin.TabularInline):
    model = charity.CharityFinancial
    extra = 1


class CharityNameInline(admin.TabularInline):
    model = charity.CharityName
    extra = 1


class CharityAdmin(JSONFieldAdmin):
    list_display = (
        "id",
        "name",
        "postcode",
        "source",
        "active",
        "date_registered",
        "date_removed",
        "income",
        "latest_fye",
    )
    list_filter = ("active", "source")
    search_fields = ["name"]
    inlines = [CharityFinancialInline, CharityNameInline]

    def view_on_site(self, obj):
        return reverse(
            "charity_html",
            kwargs={
                "regno": obj.id.replace("GB-CHC-", "")
                .replace("GB-SC-", "")
                .replace("GB-NIC-", "")
            },
        )


class VocabularyEntriesInline(admin.TabularInline):
    model = charity.VocabularyEntries
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
            kwargs["queryset"] = charity.VocabularyEntries.objects.filter(
                vocabulary=vocab
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class VocabularyAdmin(JSONFieldAdmin):
    list_display = ("title", "entries")
    inlines = [VocabularyEntriesInline]

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


admin.site.register(charity.Charity, CharityAdmin)
admin.site.register(charity.CharityRaw, JSONFieldAdmin)
admin.site.register(charity.AreaOfOperation, JSONFieldAdmin)
admin.site.register(charity.Vocabulary, VocabularyAdmin)
admin.site.register(charity.VocabularyEntries, VocabularyEntriesAdmin)
admin.site.register(charity.CcewDataFile, JSONFieldAdmin)
