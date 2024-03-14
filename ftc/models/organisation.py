import datetime
import re
from collections import defaultdict
from typing import Counter

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django_better_admin_arrayfield.models.fields import ArrayField

from ftc.models.organisation_classification import OrganisationClassification
from ftc.models.organisation_link import OrganisationLink
from ftc.models.organisation_location import OrganisationLocation
from ftc.models.orgid import OrgidField
from ftc.models.orgid_scheme import OrgidScheme

EXTERNAL_LINKS = {
    "GB-CHC": [
        [
            "https://register-of-charities.charitycommission.gov.uk/charity-details/?regId={}&subId=0",
            "Charity Commission England and Wales",
        ],
        ["https://search.charitybase.uk/chc/{}", "CharityBase"],
        # ["http://opencharities.org/charities/{}", "OpenCharities"],
        ["https://givingisgreat.org/charitydetail/?regNo={}", "Giving is Great"],
        # [
        #     "http://www.charitychoice.co.uk/charities/search?t=qsearch&q={}",
        #     "Charities Direct",
        # ],
    ],
    "GB-COH": [
        [
            "https://find-and-update.company-information.service.gov.uk/company/{}",
            "Companies House",
        ],
        ["https://opencorporates.com/companies/gb/{}", "Opencorporates"],
    ],
    "GB-NIC": [
        [
            "http://www.charitycommissionni.org.uk/charity-details/?regid={}&subid=0",
            "Charity Commission Northern Ireland",
        ],
        ["https://givingisgreat.org/charitydetail/?regNo={}", "Giving is Great"],
    ],
    "GB-SC": [
        [
            "https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number={}",
            "Office of Scottish Charity Regulator",
        ],
        ["https://givingisgreat.org/charitydetail/?regNo={}", "Giving is Great"],
    ],
    "GB-EDU": [
        [
            "https://get-information-schools.service.gov.uk/Establishments/Establishment/Details/{}",
            "Get information about schools",
        ],
    ],
    "GB-WALEDU": [
        [
            "https://mylocalschool.gov.wales/School/{}",
            "My Local School",
        ],
    ],
    "GB-UKPRN": [
        [
            "https://www.ukrlp.co.uk/ukrlp/ukrlp_provider.page_pls_provDetails?x=&pn_p_id={}&pv_status=VERIFIED&pv_vis_code=L",
            "UK Register of Learning Providers",
        ],
    ],
    "GB-NHS": [
        ["https://odsportal.hscic.gov.uk/Organisation/Details/{}", "NHS Digital"],
    ],
    "XI-GRID": [
        ["https://www.grid.ac/institutes/{}", "Global Research Identifier Database"],
    ],
    "XI-ROR": [
        ["https://ror.org/{}", "Research Organization Registry"],
    ],
    "XI-WIKIDATA": [
        ["https://www.wikidata.org/wiki/{}", "Wikidata"],
    ],
}


class Organisation(models.Model):
    org_id = OrgidField(db_index=True, verbose_name="Organisation Identifier")
    orgIDs = ArrayField(
        OrgidField(blank=True),
        verbose_name="Other organisation identifiers",
    )
    linked_orgs = ArrayField(
        models.CharField(max_length=200, blank=True),
        blank=True,
        null=True,
        verbose_name="Linked organisations",
    )
    name = models.CharField(max_length=255, verbose_name="Name")
    alternateName = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Other names",
    )
    charityNumber = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Charity number"
    )
    companyNumber = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Company number"
    )
    streetAddress = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Address: street"
    )
    addressLocality = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Address: locality"
    )
    addressRegion = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Address: region"
    )
    addressCountry = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Address: country"
    )
    postalCode = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Postcode", db_index=True
    )
    telephone = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Telephone"
    )
    email = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Email address"
    )
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    url = models.URLField(null=True, blank=True, verbose_name="Website address")
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Website domain",
    )
    latestIncome = models.BigIntegerField(
        null=True, blank=True, verbose_name="Latest income"
    )
    latestSpending = models.BigIntegerField(
        null=True, blank=True, verbose_name="Latest expenditure"
    )
    latestEmployees = models.BigIntegerField(
        null=True, blank=True, verbose_name="Latest employees"
    )
    latestVolunteers = models.BigIntegerField(
        null=True, blank=True, verbose_name="Latest volunteers"
    )
    trusteeCount = models.BigIntegerField(
        null=True, blank=True, verbose_name="Count of trustees"
    )
    latestIncomeDate = models.DateField(
        null=True, blank=True, verbose_name="Latest financial year end"
    )
    dateRegistered = models.DateField(
        null=True, blank=True, verbose_name="Date registered"
    )
    dateRemoved = models.DateField(null=True, blank=True, verbose_name="Date removed")
    active = models.BooleanField(null=True, blank=True, verbose_name="Active")
    status = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Status"
    )
    parent = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Parent organisation"
    )
    dateModified = models.DateTimeField(
        auto_now=True, verbose_name="Date record was last modified"
    )
    source = models.ForeignKey(
        "Source",
        related_name="organisations",
        on_delete=models.DO_NOTHING,
    )
    organisationType = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Other organisation types",
    )
    organisationTypePrimary = models.ForeignKey(
        "OrganisationType",
        on_delete=models.DO_NOTHING,
        related_name="organisations",
        verbose_name="Primary organisation type",
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisations",
        on_delete=models.DO_NOTHING,
    )
    priority = ArrayField(
        models.BigIntegerField(null=True, blank=True, db_index=True),
        blank=True,
        null=True,
        verbose_name="Organisation priority",
    )
    spider = models.CharField(max_length=200, db_index=True)
    org_id_scheme = models.ForeignKey(
        "OrgidScheme",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = (
            "org_id",
            "scrape",
        )
        indexes = [
            GinIndex(fields=["orgIDs"]),
            GinIndex(fields=["linked_orgs"]),
            GinIndex(fields=["alternateName"]),
            GinIndex(fields=["organisationType"]),
        ]

    def __str__(self):
        return "%s %s" % (self.organisationTypePrimary.title, self.org_id)

    @cached_property
    def org_links(self):
        return OrganisationLink.objects.filter(
            models.Q(org_id_a=self.org_id) | models.Q(org_id_b=self.org_id)
        )

    @cached_property
    def classifications(self):
        classes = (
            OrganisationClassification.objects.prefetch_related("vocabulary")
            .prefetch_related("vocabulary__vocabulary")
            .filter(org_id=self.org_id)
            .all()
        )
        return {
            vocab: [v for v in classes if v.vocabulary.vocabulary == vocab]
            for vocab in set(v.vocabulary.vocabulary for v in classes)
        }

    def get_priority(self):
        if self.org_id.scheme in OrgidScheme.PRIORITIES:
            prefix_order = OrgidScheme.PRIORITIES.index(self.org_id.scheme)
        else:
            prefix_order = len(OrgidScheme.PRIORITIES) + 1

        org_date = self.dateRegistered if self.dateRegistered else datetime.date.max
        return (
            0 if self.active else 1,
            prefix_order,
            -int("{:%Y%m%d}".format(org_date)),
        )

    @property
    def all_names(self):
        if self.name is None:
            return self.alternateName
        if self.alternateName is None:
            return [self.name]
        return [self.name] + self.alternateName

    @classmethod
    def get_fields_as_properties(cls):
        internal_fields = ["scrape", "spider", "id", "priority"]
        return [
            {"id": f.name, "name": f.verbose_name}
            for f in cls._meta.get_fields()
            if f.name not in internal_fields
        ]

    def schema_dot_org(self, request=None):
        """Return a schema.org Organisation object representing this organisation"""

        obj = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.name,
            "identifier": self.org_id,
        }

        if self.url:
            obj["url"] = self.url
        if self.description:
            obj["description"] = self.description
        if self.alternateName:
            obj["alternateName"] = self.alternateName
        if self.dateRegistered:
            obj["foundingDate"] = self.dateRegistered.isoformat()
        if not self.active and self.dateRemoved:
            obj["dissolutionDate"] = self.dateRemoved.isoformat()
        if self.orgIDs and len(self.orgIDs) > 1:
            if request:
                obj["sameAs"] = [request.build_absolute_uri(id) for id in self.sameAs]
            else:
                obj["sameAs"] = self.sameAs
            if len(obj.get("sameAs", [])) == 1:
                obj["sameAs"] = obj["sameAs"][0]
        return obj

    def _get_links(self):
        if self.url:
            yield (self.cleanUrl, self.displayUrl, self.org_id)
        if not self.orgIDs:
            return
        for o in self.orgIDs:
            links = EXTERNAL_LINKS.get(o.scheme, [])
            for link in links:
                yield (link[0].format(o.id), link[1], o)

    def get_links(self):
        links = list(self._get_links())
        link_counts = Counter(elem[1] for elem in links)
        for link in links:
            if link_counts[link[1]] > 1:
                yield (link[0], f"{link[1]} ({link[2].id})", link[2])
            else:
                yield link

    @cached_property
    def sameAs(self):
        return [
            reverse("orgid_html", kwargs=dict(org_id=o))
            for o in self.orgIDs
            if o != self.org_id
        ]

    @cached_property
    def cleanUrl(self):
        if not self.url:
            return None
        if not self.url.startswith("http") and not self.url.startswith("//"):
            return "http://" + self.url
        return self.url

    @cached_property
    def displayUrl(self):
        if not self.url:
            return None
        url = re.sub(r"(https?:)?//", "", self.url)
        if url.startswith("www."):
            url = url[4:]
        if url.endswith("/"):
            url = url[:-1]
        return url

    @cached_property
    def sortedAlternateName(self):
        if not self.alternateName:
            return []
        return sorted(
            self.alternateName,
            key=lambda x: x[4:] if x.lower().startswith("the ") else x,
        )

    def geoCodes(self):
        special_cases = {
            "K02000001": [
                "E92000001",
                "N92000002",
                "S92000003",
                "W92000004",
            ],  # United Kingdom
            # Great Britain
            "K03000001": ["E92000001", "S92000003", "W92000004"],
            "K04000001": ["E92000001", "W92000004"],  # England and Wales
        }

        for location in self.locations:
            if re.match("[ENWSK][0-9]{8}", location.geoCode):
                location_type = OrganisationLocation.LocationTypes(
                    location.locationType
                ).label
                # special case for combinations of countries
                if location.geoCode in special_cases:
                    for a in special_cases[location.geoCode]:
                        yield [location_type, a]
                    continue
                yield [location_type, location.geoCode]

    @cached_property
    def allGeoCodes(self):
        location_fields = [
            "geo_iso",
            "geo_oa11",
            "geo_oa21",
            "geo_cty",
            "geo_laua",
            "geo_ward",
            "geo_ctry",
            "geo_rgn",
            "geo_pcon",
            "geo_ttwa",
            "geo_lsoa11",
            "geo_lsoa21",
            "geo_msoa11",
            "geo_msoa21",
            "geo_lep1",
            "geo_lep2",
        ]

        locations = set()
        for location in self.locations:
            for f in location_fields:
                value = getattr(location, f, None)
                if value and not value.endswith("999999"):
                    locations.add(value)
        return list(locations)

    @cached_property
    def locations(self):
        return OrganisationLocation.objects.filter(org_id=self.org_id).all()

    @cached_property
    def location(self):
        locations = []
        for location in self.locations:
            if location.geoCodeType == OrganisationLocation.GeoCodeTypes.POSTCODE:
                geocode = location.geo_laua
            else:
                geocode = location.geoCode
            locations.append(
                {
                    "id": location.geoCode,
                    "name": location.name,
                    "geoCode": geocode,
                    "type": location.locationType,
                }
            )
        return locations

    @cached_property
    def lat_lngs(self):
        return_lat_lngs = []
        for location in self.locations:
            if location.geo_lat and location.geo_long:
                location_type = OrganisationLocation.LocationTypes(
                    location.locationType
                ).label
                return_lat_lngs.append(
                    (location.geo_lat, location.geo_long, location_type, location.name)
                )
        return return_lat_lngs

    @cached_property
    def hq(self):
        for location in self.locations:
            if (
                location.locationType
                == OrganisationLocation.LocationTypes.REGISTERED_OFFICE
            ):
                return location

    def locations_group(self):
        locations = defaultdict(lambda: defaultdict(set))

        for location in self.locations:
            location_type = OrganisationLocation.LocationTypes(
                location.locationType
            ).label
            if (
                location.geoCodeType == OrganisationLocation.GeoCodeTypes.POSTCODE
                and location.geo_laua
            ):
                locations[location_type][location.geo_iso].add(location.geo_laua)
            elif location.geoCode:
                locations[location_type][location.geo_iso].add(location.geoCode)
        return locations

    def __getattr__(self, name):
        if name.startswith("geo_"):
            return getattr(self.hq, name, None)
        return super().__getattr__(name)
