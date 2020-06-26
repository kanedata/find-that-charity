from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from prettyjson.widgets import PrettyJSONWidget

import charity.models as charity


class JSONFieldAdmin(admin.ModelAdmin):
    list_per_page = 20
    formfield_overrides = {
        JSONField: {"widget": PrettyJSONWidget(attrs={"initial": "parsed"})}
    }


class CharityFinancialInline(admin.TabularInline):
    model = charity.CharityFinancial
    extra = 1

class CharityNameInline(admin.TabularInline):
    model = charity.CharityName
    extra = 1


class CharityAdmin(JSONFieldAdmin):
    list_display = ('id', 'name', 'postcode', 'source',
                    'active', 'date_registered', 'date_removed', 'income', 'latest_fye')
    list_filter = ('active', 'source')
    search_fields = ['name']
    inlines = [CharityFinancialInline, CharityNameInline]

    def view_on_site(self, obj):
        url = reverse('charity_html', kwargs={'regno': obj.id.replace('GB-CHC-', '').replace('GB-SC-', '').replace('GB-NIC-', '')})
        return url

admin.site.register(charity.Charity, CharityAdmin)
admin.site.register(charity.CharityRaw, JSONFieldAdmin)
admin.site.register(charity.AreaOfOperation, JSONFieldAdmin)
admin.site.register(charity.Vocabulary, JSONFieldAdmin)
admin.site.register(charity.VocabularyEntries, JSONFieldAdmin)
admin.site.register(charity.CcewDataFile, JSONFieldAdmin)
