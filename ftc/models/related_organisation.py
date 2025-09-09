import math

from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property

from ftc.models.organisation import EXTERNAL_LINKS, Organisation
from ftc.models.organisation_link import OrganisationLink
from ftc.models.organisation_location import OrganisationLocation
from ftc.models.organisation_type import OrganisationType
from ftc.models.source import Source

SCALE_DEFAULT = 1.0
SCALE_MINIMUM = 0.1
SCALE_INACTIVE = 0.7
SCALE_BIG_ORGANISATION = 16
BIG_ORGTYPES = ["local-authority", "university", "government-organisation"]


class RelatedOrganisation:
    def __init__(self, orgs):
        self.records = self.prioritise_orgs(orgs)

    @classmethod
    def from_orgid(cls, org_id):
        orgs = Organisation.objects.filter(linked_orgs__contains=[org_id])
        return cls(orgs)

    @cached_property
    def orgIDs(self):
        return list(set(self.get_all("orgIDs")))

    @cached_property
    def names(self):
        names = {}
        for r in self.records:
            for n in r.all_names:
                if n not in names or not n.isupper() or not n.islower():
                    names[n.lower().strip()] = n
        return names

    @cached_property
    def alternateName(self):
        names = self.get_all("all_names")
        return list(
            set(
                [
                    self.names.get(n.lower().strip(), n)
                    for n in names
                    if n.lower().strip() != self.name.lower().strip()
                ]
            )
        )

    @cached_property
    def name(self):
        return self.names.get(self.records[0].name.lower(), self.records[0].name)

    @cached_property
    def sources(self):
        return list(Source.objects.filter(id__in=self.source_ids).all())

    @cached_property
    def parents(self):
        parents = [parent_id for parent_id in self.get_all("parent") if parent_id]
        return Organisation.objects.filter(org_id__in=parents).exclude(
            orgIDs__overlap=self.orgIDs
        )

    @cached_property
    def children(self):
        return Organisation.objects.filter(parent__in=self.orgIDs)

    @cached_property
    def source_ids(self):
        sources = list(self.get_all("source_id"))
        sources.extend(
            list(
                OrganisationLink.objects.filter(
                    Q(org_id_a__in=self.orgIDs) | Q(org_id_b__in=self.orgIDs)
                ).values_list("source_id", flat=True)
            )
        )
        return list(set(sources))

    @cached_property
    def locations(self):
        return OrganisationLocation.objects.filter(org_id__in=self.orgIDs)

    def hq_region(self, areatype):
        for location in self.locations:
            if (
                location.locationType
                != OrganisationLocation.LocationTypes.REGISTERED_OFFICE
            ):
                continue
            return getattr(location, f"geo_{areatype}", None)

    @cached_property
    def geocodes(self):
        location_fields = [
            "geo_iso",
            # "geo_oa11",
            # "geo_oa21",
            "geo_cty",
            "geo_laua",
            "geo_ward",
            "geo_ctry",
            "geo_rgn",
            "geo_pcon",
            # "geo_ttwa",
            "geo_lsoa11",
            "geo_lsoa21",
            "geo_msoa11",
            "geo_msoa21",
            # "geo_lep1",
            # "geo_lep2",
        ]
        geocodes = set()
        for location in self.locations:
            for field in location_fields:
                value = getattr(location, field, None)
                if value and not value.endswith("999999"):
                    geocodes.add(value)
        return list(geocodes)

    @cached_property
    def org_links(self):
        return list(
            set(
                OrganisationLink.objects.filter(
                    Q(org_id_a__in=self.orgIDs) | Q(org_id_b__in=self.orgIDs)
                )
            )
        )

    @cached_property
    def search_scale(self):
        scaling = SCALE_DEFAULT
        income_vals = [
            max([income, 1]) for income in self.get_all("latestIncome") if income
        ]

        if income_vals:
            scaling = math.log(max(income_vals)) + 1

        if (
            scaling == SCALE_DEFAULT
            and self.organisationTypePrimary.slug in BIG_ORGTYPES
        ):
            scaling = SCALE_BIG_ORGANISATION

        if not self.active:
            scaling = scaling * SCALE_INACTIVE

        if not scaling or scaling < SCALE_MINIMUM:
            return SCALE_MINIMUM

        return scaling

    def __getattr__(self, key, *args):
        return getattr(self.records[0], key, *args)

    def first(self, field, justvalue=False):
        for r in self.records:
            if getattr(r, field, None):
                if justvalue:
                    return getattr(r, field)
                return {
                    "value": getattr(r, field),
                    "orgid": r.org_id,
                    "source": r.source,
                }
        if justvalue:
            return None
        return {}

    def get_all(self, field):
        seen = set()
        for r in self.records:
            values = getattr(r, field, None)
            if not isinstance(values, list):
                values = [values]
            for v in values:
                if v not in seen:
                    yield v
                seen.add(v)

    def prioritise_orgs(self, orgs):
        # Decide what order a list of organisations should go in,
        # based on their priority
        return sorted(orgs, key=lambda o: o.get_priority())

    def get_links(self):
        links_seen = set()
        for r in self.records:
            for link in r.get_links():
                if link[1] not in links_seen:
                    yield link
                links_seen.add(link[1])

    def recordsBySource(self, source_id):
        return [r for r in self.records if r.source_id == source_id]

    def org_linksBySource(self, source_id):
        return [r for r in self.org_links if r.source_id == source_id]

    @cached_property
    def sameAs(self):
        return [
            reverse("orgid_html", kwargs=dict(org_id=o))
            for o in self.orgIDs
            if o != self.org_id
        ]

    @cached_property
    def activeRecords(self):
        return [r for r in self.records if r.active]

    @cached_property
    def inactiveRecords(self):
        return [r for r in self.records if not r.active]

    def schema_dot_org(self, request=None):
        """Return a schema.org Organisation object representing this organisation"""

        obj = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": self.name,
            "identifier": self.org_id,
        }

        if self.first("url"):
            obj["url"] = self.first("url").get("value")
        if self.first("description"):
            obj["description"] = self.first("description").get("value")
        if self.alternateName:
            obj["alternateName"] = self.alternateName
        if self.dateRegistered:
            obj["foundingDate"] = self.dateRegistered.isoformat()
        if not self.active and self.first("dateRemoved"):
            obj["dissolutionDate"] = self.first("dateRemoved").get("value").isoformat()
        if len(self.orgIDs) > 1:
            if request:
                obj["sameAs"] = [request.build_absolute_uri(id) for id in self.sameAs]
            else:
                obj["sameAs"] = self.sameAs
            if len(obj.get("sameAs", [])) == 1:
                obj["sameAs"] = obj["sameAs"][0]
        return obj

    def to_json(self, as_charity=False, request=None, charity=None):
        address_fields = [
            "streetAddress",
            "addressLocality",
            "addressRegion",
            "addressCountry",
            "postalCode",
        ]
        orgtypes = [y for y in self.get_all("organisationType")]
        orgtypes = [o.title for o in OrganisationType.objects.filter(slug__in=orgtypes)]

        def build_url(url):
            if request:
                return request.build_absolute_uri(url)
            return url

        if as_charity:
            ccew_number = None
            ccew_link = None
            oscr_number = None
            oscr_link = None
            ccni_number = None
            ccni_link = None
            company_numbers = []
            if self.linked_orgs:
                for o in self.linked_orgs:
                    if o.startswith("GB-CHC-"):
                        ccew_number = o.replace("GB-CHC-", "")
                        ccew_link = EXTERNAL_LINKS["GB-CHC"][1][0].format(ccew_number)
                    elif o.startswith("GB-NIC-"):
                        ccni_number = o.replace("GB-NIC-", "")
                        ccni_link = EXTERNAL_LINKS["GB-NIC"][0][0].format(ccni_number)
                    elif o.startswith("GB-SC-"):
                        oscr_number = o.replace("GB-SC-", "")
                        oscr_link = EXTERNAL_LINKS["GB-SC"][0][0].format(oscr_number)
                    elif o.startswith("GB-COH-"):
                        company_numbers.append(
                            {
                                "number": o.replace("GB-COH-", ""),
                                "url": EXTERNAL_LINKS["GB-COH"][0][0].format(
                                    o.replace("GB-COH-", "")
                                ),
                                "source": self.source.id,
                            }
                        )
            names = []
            names_seen = set()
            for r in self.records:
                if r.name not in names_seen:
                    names.append(
                        {
                            "name": r.name,
                            "type": "registered name",
                            "source": r.source.id,
                        }
                    )
                    names_seen.add(r.name)
                if r.alternateName:
                    for n in r.alternateName:
                        if n not in names_seen:
                            names.append(
                                {"name": n, "type": "other name", "source": r.source.id}
                            )
                            names_seen.add(n)

            return {
                "ccew_number": ccew_number,
                "oscr_number": oscr_number,
                "ccni_number": ccni_number,
                "active": self.active,
                "names": names,
                "known_as": self.name,
                "geo": {
                    "areas": [],
                    "postcode": self.postalCode,
                    "location": self.location,
                    "address": {
                        k: getattr(self, k)
                        for k in address_fields
                        if getattr(self, k, None)
                    },
                },
                "url": self.cleanUrl,
                "domain": self.domain,
                "latest_income": self.latestIncome,
                "company_number": company_numbers,
                "parent": self.parent,
                "ccew_link": ccew_link,
                "oscr_link": oscr_link,
                "ccni_link": ccni_link,
                "date_registered": self.dateRegistered,
                "date_removed": self.dateRemoved,
                "org-ids": self.linked_orgs,
                "alt_names": self.alternateName,
                "last_modified": self.dateModified,
            }

        return {
            "id": self.org_id,
            "name": self.name,
            "charityNumber": self.charityNumber,
            "companyNumber": self.companyNumber,
            "description": self.description,
            "url": self.cleanUrl,
            "latestFinancialYearEnd": self.latestIncomeDate,
            "latestIncome": self.latestIncome,
            "latestSpending": self.latestSpending,
            "latestEmployees": self.latestEmployees,
            "latestVolunteers": self.latestVolunteers,
            "trusteeCount": self.trusteeCount,
            "dateRegistered": self.dateRegistered,
            "dateRemoved": self.dateRemoved,
            "active": self.active,
            "parent": self.parent,
            "organisationType": orgtypes,
            "organisationTypePrimary": self.organisationTypePrimary.title,
            "alternateName": self.alternateName,
            "telephone": None,
            "email": None,
            "location": self.location,
            "address": {
                k: getattr(self, k) for k in address_fields if getattr(self, k, None)
            },
            "sources": [s.id for s in self.sources],
            "links": [
                {
                    "site": "Find that Charity",
                    "url": build_url(
                        reverse("orgid_json", kwargs={"org_id": self.org_id})
                    ),
                    "orgid": self.org_id,
                },
            ]
            + [
                {"site": link[1], "url": link[0], "orgid": link[2]}
                for link in self.get_links()
            ],
            "orgIDs": self.orgIDs,
            "linked_records": [
                {
                    "orgid": orgid,
                    "url": build_url(reverse("orgid_json", kwargs={"org_id": orgid})),
                }
                for orgid in self.linked_orgs
            ]
            if self.linked_orgs
            else [],
            "dateModified": self.dateModified,
        }
