from rest_framework import serializers

from ftc.models import Organisation, OrganisationType


class OrganisationSerializer(serializers.HyperlinkedModelSerializer):
    organisationTypePrimary = serializers.HyperlinkedRelatedField(
        view_name='organisation-types-detail',
        lookup_field='slug',
        lookup_url_kwarg='slug',
        read_only=True,
    )
    org_id_scheme = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Organisation
        fields = [
            "org_id",
            "orgIDs",
            "linked_orgs",
            "name",
            "alternateName",
            "charityNumber",
            "companyNumber",
            "streetAddress",
            "addressLocality",
            "addressRegion",
            "addressCountry",
            "postalCode",
            "telephone",
            "email",
            "description",
            "url",
            "domain",
            "latestIncome",
            "latestIncomeDate",
            "dateRegistered",
            "dateRemoved",
            "active",
            "status",
            "parent",
            "dateModified",
            # "source",
            "organisationType",
            "organisationTypePrimary",
            # "scrape",
            # "spider",
            "location",
            "org_id_scheme",
            # geography fields
            "geo_oa11",
            "geo_cty",
            "geo_laua",
            "geo_ward",
            "geo_ctry",
            "geo_rgn",
            "geo_pcon",
            "geo_ttwa",
            "geo_lsoa11",
            "geo_msoa11",
            "geo_lep1",
            "geo_lep2",
            "geo_lat",
            "geo_long",
        ]


class OrganisationTypeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = OrganisationType
        fields = [
            "slug",
            "title",
        ]
