import datetime
import re

from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_better_admin_arrayfield.models.fields import ArrayField

IGNORE_DOMAINS = (
    "gmail.com",
    "hotmail.com",
    "btinternet.com",
    "hotmail.co.uk",
    "yahoo.co.uk",
    "outlook.com",
    "aol.com",
    "btconnect.com",
    "yahoo.com",
    "googlemail.com",
    "ntlworld.com",
    "talktalk.net",
    "sky.com",
    "live.co.uk",
    "ntlworld.com",
    "tiscali.co.uk",
    "icloud.com",
    "btopenworld.com",
    "blueyonder.co.uk",
    "virginmedia.com",
    "nhs.net",
    "me.com",
    "msn.com",
    "talk21.com",
    "aol.co.uk",
    "mail.com",
    "live.com",
    "virgin.net",
    "ymail.com",
    "mac.com",
    "waitrose.com",
    "gmail.co.uk",
)


EXTERNAL_LINKS = {
    "GB-CHC": [
        ["https://ccew.dkane.net/charity/{}", "Charity Commission England and Wales"],
        ["https://charitybase.uk/charities/{}", "CharityBase"],
        ["http://opencharities.org/charities/{}", "OpenCharities"],
        ["http://www.guidestar.org.uk/summary.aspx?CCReg={}", "GuideStar"],
        [
            "http://www.charitychoice.co.uk/charities/search?t=qsearch&q={}",
            "Charities Direct",
        ],
    ],
    "GB-COH": [
        ["https://beta.companieshouse.gov.uk/company/{}", "Companies House"],
        ["https://opencorporates.com/companies/gb/{}", "Opencorporates"],
    ],
    "GB-NIC": [
        [
            "http://www.charitycommissionni.org.uk/charity-details/?regid={}&subid=0",
            "Charity Commission Northern Ireland",
        ],
    ],
    "GB-SC": [
        [
            "https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number={}",
            "Office of Scottish Charity Regulator",
        ],
    ],
    "GB-EDU": [
        [
            "https://get-information-schools.service.gov.uk/Establishments/Establishment/Details/{}",
            "Get information about schools",
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
    "GB-LAE": [
        [
            "https://www.registers.service.gov.uk/registers/local-authority-eng/records/{}",
            "Local authorities in England",
        ],
    ],
    "GB-LAN": [
        [
            "https://www.registers.service.gov.uk/registers/local-authority-nir/records/{}",
            "Local authorities in Northern Ireland",
        ],
    ],
    "GB-LAS": [
        [
            "https://www.registers.service.gov.uk/registers/local-authority-sct/records/{}",
            "Local authorities in Scotland",
        ],
    ],
    "GB-PLA": [
        [
            "https://www.registers.service.gov.uk/registers/principal-local-authority/records/{}",
            "Principal Local authorities in Wales",
        ],
    ],
    "GB-GOR": [
        [
            "https://www.registers.service.gov.uk/registers/government-organisation/records/{}",
            "Government organisations on GOV.UK",
        ],
    ],
    "XI-GRID": [
        ["https://www.grid.ac/institutes/{}", "Global Research Identifier Database"],
    ],
}


class Orgid(str):
    def __new__(cls, content):
        instance = super().__new__(cls, content)
        instance._split_orgid(content)
        return instance

    def _split_orgid(self, value):
        self.scheme = None
        self.id = value
        if value is None:
            return
        split_orgid = value.split("-", maxsplit=3)
        if len(split_orgid) > 2:
            self.scheme = "-".join(split_orgid[:2])
            self.id = "-".join(split_orgid[2:])


class OrgidField(models.CharField):

    description = "An orgid based on the format here: http://org-id.guide/about"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 200
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Orgid(value)

    def to_python(self, value):
        if isinstance(value, Orgid):
            return value

        if value is None:
            return value

        return Orgid(value)


class Organisation(models.Model):
    org_id = OrgidField(db_index=True, verbose_name="Organisation Identifier")
    orgIDs = ArrayField(
        OrgidField(blank=True),
        verbose_name="Other organisation identifiers",
    )
    linked_orgs = ArrayField(
        models.CharField(max_length=100, blank=True),
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
        on_delete=models.CASCADE,
    )
    organisationType = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Other organisation types",
    )
    organisationTypePrimary = models.ForeignKey(
        "OrganisationType",
        on_delete=models.CASCADE,
        related_name="organisations",
        verbose_name="Primary organisation type",
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisations",
        on_delete=models.CASCADE,
    )
    spider = models.CharField(max_length=200, db_index=True)
    location = models.JSONField(null=True, blank=True)
    org_id_scheme = models.ForeignKey(
        "OrgidScheme",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    # geography fields
    geo_oa11 = models.CharField(max_length=9, null=True, blank=True)
    geo_cty = models.CharField(max_length=9, null=True, blank=True)
    geo_laua = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_ward = models.CharField(max_length=9, null=True, blank=True)
    geo_ctry = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_rgn = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_pcon = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_ttwa = models.CharField(max_length=9, null=True, blank=True)
    geo_lsoa11 = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_msoa11 = models.CharField(max_length=9, null=True, blank=True, db_index=True)
    geo_lep1 = models.CharField(max_length=9, null=True, blank=True)
    geo_lep2 = models.CharField(max_length=9, null=True, blank=True)
    geo_lat = models.FloatField(null=True, blank=True)
    geo_long = models.FloatField(null=True, blank=True)

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

    @property
    def org_links(self):
        return OrganisationLink.objects.filter(
            models.Q(org_id_a=self.org_id) | models.Q(org_id_b=self.org_id)
        )

    def get_priority(self):
        if self.org_id.scheme in OrgidScheme.PRIORITIES:
            prefix_order = OrgidScheme.PRIORITIES.index(self.org_id.scheme)
        else:
            prefix_order = len(OrgidScheme.PRIORITIES) + 1
        return (
            0 if self.active else 1,
            prefix_order,
            self.dateRegistered if self.dateRegistered else datetime.date.min,
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
        internal_fields = ["scrape", "spider", "id"]
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
        return obj

    def get_links(self):
        if self.url:
            yield (self.cleanUrl, "Organisation Website")
        if not self.orgIDs:
            return
        for o in self.orgIDs:
            links = EXTERNAL_LINKS.get(o.scheme, [])
            for link in links:
                yield (link[0].format(o.id), link[1])

    @property
    def sameAs(self):
        return [
            reverse("orgid_html", kwargs=dict(org_id=o))
            for o in self.orgIDs
            if o != self.org_id
        ]

    @property
    def cleanUrl(self):
        if not self.url:
            return None
        if not self.url.startswith("http") and not self.url.startswith("//"):
            return "http://" + self.url
        return self.url

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

        for v in self.location:
            if v.get("geoCode") and re.match("[ENWSK][0-9]{8}", v.get("geoCode")):
                # special case for combinations of countries
                if v["geoCode"] in special_cases:
                    for a in special_cases[v["geoCode"]]:
                        yield a
                    continue
                yield v.get("geoCode")


class OrganisationType(models.Model):
    slug = models.SlugField(max_length=255, editable=False, primary_key=True)
    title = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    KEY_TYPES = [
        "registered-charity",
        "registered-charity-england-and-wales",
        "registered-charity-scotland",
        "registered-charity-northern-ireland",
        "registered-company",
        # "company limited by guarantee",
        "charitable-incorporated-organisation",
        "education",
        "community-interest-company",
        "health",
        "registered-society",
        "community-amateur-sports-club",
        "registered-provider-of-social-housing",
        "government-organisation",
        "local-authority",
        "university",
    ]

    def is_keytype(self):
        return self.slug in self.KEY_TYPES

    def __str__(self):
        return self.title


class OrganisationLink(models.Model):
    org_id_a = OrgidField(max_length=255, db_index=True)
    org_id_b = OrgidField(max_length=255, db_index=True)
    spider = models.CharField(max_length=200, db_index=True)
    source = models.ForeignKey(
        "Source",
        related_name="organisation_links",
        on_delete=models.CASCADE,
    )
    scrape = models.ForeignKey(
        "Scrape",
        related_name="organisation_links",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return "From {} to {}".format(self.org_id_a, self.org_id_b)


class Source(models.Model):
    id = models.CharField(max_length=200, unique=True, db_index=True, primary_key=True)
    data = models.JSONField()

    @property
    def title(self):
        return self.data.get("title")

    @property
    def publisher(self):
        return self.data.get("publisher", {}).get("name")

    @property
    def slug(self):
        return self.id

    def __str__(self):
        return self.publisher + " (" + self.title + ")"


class Scrape(models.Model):
    class ScrapeStatus(models.TextChoices):
        RUNNING = "running", "In progress"
        SUCCESS = "success", "Finished successfully"
        ERRORS = "errors", "Finished with errors"
        FAILED = "failed", "Failed to complete"

    spider = models.CharField(max_length=200)
    result = models.JSONField(null=True, blank=True, editable=False)
    start_time = models.DateTimeField(auto_now_add=True, editable=False)
    finish_time = models.DateTimeField(
        auto_now=True, null=True, blank=True, editable=False
    )
    log = models.TextField(null=True, blank=True, editable=False)
    items = models.IntegerField(default=0, editable=False)
    errors = models.IntegerField(default=0, editable=False)
    status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=ScrapeStatus.choices,
        editable=False,
    )

    def __str__(self):
        return "{} [{}] {:%Y-%m-%d %H:%M}".format(
            self.spider, self.status, self.start_time
        )


class OrgidScheme(models.Model):

    PRIORITIES = [
        "GB-CHC",
        "GB-SC",
        "GB-NIC",
        "GB-EDU",
        "GB-LAE",
        "GB-PLA",
        "GB-LAS",
        "GB-LANI",
        "GB-GOR",
        "GB-COH",
    ]

    code = models.CharField(max_length=200, primary_key=True, db_index=True)
    data = models.JSONField()
    priority = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.code in self.PRIORITIES:
            self.priority = self.PRIORITIES.index(self.code)
        else:
            self.priority = len(self.PRIORITIES) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "{} - {}".format(self.code, self.data.get("name", {}).get("en"))


class RelatedOrganisation:
    def __init__(self, orgs):
        self.records = self.prioritise_orgs(orgs)

    @classmethod
    def from_orgid(cls, org_id):
        orgs = Organisation.objects.filter(linked_orgs__contains=[org_id])
        return cls(orgs)

    @property
    def orgIDs(self):
        return list(set(self.get_all("orgIDs")))

    @property
    def names(self):
        names = {}
        for r in self.records:
            for n in r.all_names:
                if n not in names or not n.isupper() or not n.islower():
                    names[n.lower().strip()] = n
        return names

    @property
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

    @property
    def name(self):
        return self.names.get(self.records[0].name.lower(), self.records[0].name)

    @property
    def sources(self):
        sources = list(self.get_all("source"))
        sources.extend([o.source for o in self.org_links])
        return list(set(sources))

    @property
    def org_links(self):
        org_links = []
        for o in self.records:
            org_links.extend(o.org_links)
        return list(set(org_links))

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

    @property
    def sameAs(self):
        return [
            reverse("orgid_html", kwargs=dict(org_id=o))
            for o in self.orgIDs
            if o != self.org_id
        ]

    @property
    def activeRecords(self):
        return [r for r in self.records if r.active]

    @property
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
        return obj

    def to_json(self, charity=False):
        address_fields = [
            "streetAddress",
            "addressLocality",
            "addressRegion",
            "addressCountry",
            "postalCode",
        ]
        orgtypes = [y for y in self.get_all("organisationType")]
        orgtypes = [o.title for o in OrganisationType.objects.filter(slug__in=orgtypes)]

        if charity:
            ccew_number = None
            ccew_link = None
            oscr_number = None
            oscr_link = None
            ccni_number = None
            ccni_link = None
            company_numbers = []
            for o in self.orgIDs:
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
                },
                "url": self.url,
                "domain": self.domain,
                "latest_income": self.latestIncome,
                "company_number": company_numbers,
                "parent": self.parent,
                "ccew_link": ccew_link,
                "oscr_link": oscr_link,
                "ccni_link": ccni_link,
                "date_registered": self.dateRegistered,
                "date_removed": self.dateRemoved,
                "org-ids": self.orgIDs,
                "alt_names": self.alternateName,
                "last_modified": self.dateModified,
            }

        return {
            "sources": [s.id for s in self.sources],
            "name": self.name,
            "charityNumber": self.charityNumber,
            "companyNumber": self.companyNumber,
            "telephone": self.telephone,
            "email": self.email,
            "description": self.description,
            "url": self.url,
            "latestIncome": self.latestIncome,
            "dateModified": self.dateModified,
            "dateRegistered": self.dateRegistered,
            "dateRemoved": self.dateRemoved,
            "active": self.active,
            "parent": self.parent,
            "organisationType": orgtypes,
            "organisationTypePrimary": self.organisationTypePrimary.title,
            "alternateName": self.alternateName,
            "orgIDs": self.orgIDs,
            "id": self.org_id,
            "location": self.location,
            "address": {
                k: getattr(self, k) for k in address_fields if getattr(self, k, None)
            },
        }
