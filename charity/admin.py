from django.contrib import admin
from django.db import models
from django.urls import reverse
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


admin.site.register(charity.Charity, CharityAdmin)
admin.site.register(charity.CharityRaw, JSONFieldAdmin)
admin.site.register(charity.AreaOfOperation, JSONFieldAdmin)
