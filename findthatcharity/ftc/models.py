import operator

from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.utils.text import slugify
from dbview.models import DbView

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

class Organisation(models.Model):
    org_id = models.CharField(max_length=200, db_index=True)
    orgIDs = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
    )
    linked_orgs = ArrayField(
        models.CharField(max_length=100, blank=True),
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    alternateName = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
    )
    charityNumber = models.CharField(max_length=255, null=True, blank=True)
    companyNumber = models.CharField(max_length=255, null=True, blank=True)
    streetAddress = models.CharField(max_length=255, null=True, blank=True)
    addressLocality = models.CharField(max_length=255, null=True, blank=True)
    addressRegion = models.CharField(max_length=255, null=True, blank=True)
    addressCountry = models.CharField(max_length=255, null=True, blank=True)
    postalCode = models.CharField(max_length=255, null=True, blank=True)
    telephone = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    latestIncome = models.BigIntegerField(null=True, blank=True)
    latestIncomeDate = models.DateField(null=True, blank=True)
    dateRegistered = models.DateField(null=True, blank=True)
    dateRemoved = models.DateField(null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    parent = models.CharField(max_length=200, null=True, blank=True)
    dateModified = models.DateTimeField(auto_now=True)
    source = models.ForeignKey(
        'Source',
        on_delete=models.CASCADE,
    )
    organisationType = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
    )
    organisationTypePrimary = models.ForeignKey(
        'OrganisationType',
        on_delete=models.CASCADE,
        related_name="+",
    )
    scrape = models.ForeignKey(
        'Scrape',
        on_delete=models.CASCADE,
    )
    spider = models.CharField(max_length=200, db_index=True)
    location = JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('org_id', 'scrape',)
        indexes = [
            GinIndex(fields=["orgIDs"]),
            GinIndex(fields=["linked_orgs"]),
            GinIndex(fields=["alternateName"]),
            GinIndex(fields=["organisationType"]),
        ]

    def __str__(self):
        return '%s %s' % (self.organisationTypePrimary.title, self.org_id)

    @staticmethod
    def get_orgid_prefix(org_id):
        return "-".join(org_id.split("-")[0:2])

    def org_links(self):
        return OrganisationLink.objects.filter(
            models.Q(org_id_a=self.org_id) |
            models.Q(org_id_b=self.org_id)
        )

class OrganisationType(models.Model):
    slug = models.SlugField(max_length=255, editable=False, primary_key=True)
    title = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

    KEY_TYPES = [
        # "registered-charity",
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

class OrganisationLink(models.Model):
    org_id_a = models.CharField(max_length=255, db_index=True)
    org_id_b = models.CharField(max_length=255, db_index=True)
    spider = models.CharField(max_length=200, db_index=True)
    source = models.ForeignKey(
        'Source',
        on_delete=models.CASCADE,
    )
    scrape = models.ForeignKey(
        'Scrape',
        on_delete=models.CASCADE,
    )

class Source(models.Model):
    id = models.CharField(max_length=200, unique=True,
                          db_index=True, primary_key=True)
    data = JSONField()


class Scrape(models.Model):

    class ScrapeStatus(models.TextChoices):
        RUNNING = 'running', 'In progress'
        SUCCESS = 'success', 'Finished successfully'
        ERRORS = 'errors', 'Finished with errors'
        FAILED = 'failed', 'Failed to complete'

    spider = models.CharField(max_length=200)
    result = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    finish_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    log = models.TextField(null=True, blank=True)
    items = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    status = models.CharField(max_length=50, null=True,
                              blank=True, choices=ScrapeStatus.choices)
    

class LinkedOrganisation(DbView):
    org_id_a = models.CharField(max_length=255)
    org_id_b = models.CharField(max_length=255)

    @classmethod
    def view(cl):
        '''
        This method returns the SQL string that creates the view, in this
        example fieldB is the result of annotating another column
        '''
        qs = OrganisationLink.objects.all().\
            values('org_id_a', 'org_id_b')
        qs = qs.union(
            OrganisationLink.objects.all().\
            values('org_id_b', 'org_id_a'),
        )
        qs = qs.union(
            OrganisationLink.objects.all().
            values('org_id_a', 'org_id_a'),
        )
        qs = qs.union(
            OrganisationLink.objects.all().
            values('org_id_b', 'org_id_b'),
        )
        return str(qs.query)


class RelatedOrganisation:

    EXTERNAL_LINKS = {
        "GB-CHC": [
            ["http://apps.charitycommission.gov.uk/Showcharity/RegisterOfCharities/SearchResultHandler.aspx?RegisteredCharityNumber={}&SubsidiaryNumber=0&Ref=CO",
             "Charity Commission England and Wales"],
            ["http://beta.charitycommission.gov.uk/charity-details/?regid={}&subid=0",
             "Charity Commission England and Wales (beta)"],
            ["https://charitybase.uk/charities/{}", "CharityBase"],
            ["http://opencharities.org/charities/{}", "OpenCharities"],
            ["http://www.guidestar.org.uk/summary.aspx?CCReg={}", "GuideStar"],
            ["http://www.charitychoice.co.uk/charities/search?t=qsearch&q={}",
             "Charities Direct"],
            ["https://olib.uk/charity/html/{}", "CharityData by Olly Benson"],
        ],
        "GB-COH": [
            ["https://beta.companieshouse.gov.uk/company/{}", "Companies House"],
            ["https://opencorporates.com/companies/gb/{}", "Opencorporates"],
        ],
        "GB-NIC": [
            ["http://www.charitycommissionni.org.uk/charity-details/?regid={}&subid=0",
             "Charity Commission Northern Ireland"],
        ],
        "GB-SC": [
            ["https://www.oscr.org.uk/about-charities/search-the-register/charity-details?number={}",
             "Office of Scottish Charity Regulator"],
        ],
        "GB-EDU": [
            ["https://get-information-schools.service.gov.uk/Establishments/Establishment/Details/{}",
             "Get information about schools"],
        ],
        "GB-NHS": [
            ["https://odsportal.hscic.gov.uk/Organisation/Details/{}", "NHS Digital"],
        ],
        "GB-LAE": [
            ["https://www.registers.service.gov.uk/registers/local-authority-eng/records/{}",
             "Local authorities in England"],
        ],
        "GB-LAN": [
            ["https://www.registers.service.gov.uk/registers/local-authority-nir/records/{}",
             "Local authorities in Northern Ireland"],
        ],
        "GB-LAS": [
            ["https://www.registers.service.gov.uk/registers/local-authority-sct/records/{}",
             "Local authorities in Scotland"],
        ],
        "GB-PLA": [
            ["https://www.registers.service.gov.uk/registers/principal-local-authority/records/{}",
             "Principal Local authorities in Wales"],
        ],
        "GB-GOR": [
            ["https://www.registers.service.gov.uk/registers/government-organisation/records/{}",
             "Government organisations on GOV.UK"],
        ],
        "XI-GRID": [
            ["https://www.grid.ac/institutes/{}",
             "Global Research Identifier Database"],
        ],
    }

    def __init__(self, orgs):
        self.records = self.prioritise_orgs(orgs)
        self.orgIDs = set(self.get_all("orgIDs"))
        self.alternateName = list(self.get_all("alternateName"))
        self.sources = list(self.get_all("source"))

        self.org_links = []
        for o in self.records:
            self.org_links.extend(o.org_links())
        self.org_links = list(set(self.org_links))
        self.sources.extend(list(set([o.source for o in self.org_links])))
        self.sources = list(set(self.sources))

    def __getattr__(self, key, *args):
        return getattr(self.records[0], key, *args)

    def first(self, field):
        for r in self.records:
            if getattr(r, field, None):
                return {
                    "value": getattr(r, field),
                    "orgid": r.org_id,
                    "source": r.source,
                }

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
        if len(orgs) == 1:
            return orgs

        def get_priority_fields(o):
            prefix = Organisation.get_orgid_prefix(o.org_id)
            if prefix in PRIORITIES:
                prefix_order = PRIORITIES.index(prefix)
            else:
                prefix_order = len(PRIORITIES) + 1
            return (
                o.org_id,
                prefix,
                prefix_order,
                o.dateRegistered,
            )

        orgs = {o.org_id: o for o in orgs}

        to_prioritise = sorted(
            [get_priority_fields(o) for o in orgs.values() if o.active],
            key=operator.itemgetter(2, 3)
        ) + sorted(
            [get_priority_fields(o) for o in orgs.values() if not o.active],
            key=operator.itemgetter(2, 3)
        )
        return [orgs[p[0]] for p in to_prioritise]

    def get_links(self):
        if self.url:
            yield (self.url, 'Organisation Website')
        for o in self.orgIDs:
            for prefix, ls in self.EXTERNAL_LINKS.items():
                if o.startswith(prefix + "-"):
                    regno = o.replace(prefix + "-", "")
                    for l in ls:
                        yield (l[0].format(regno), l[1])
