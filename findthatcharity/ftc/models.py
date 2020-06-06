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

    @staticmethod
    def prioritise_orgs(orgs):
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
                PRIORITIES.index(Organisation.get_orgid_prefix(o.org_id)),
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


class OrganisationType(models.Model):
    slug = models.SlugField(max_length=255, editable=False, primary_key=True)
    title = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        value = self.title
        self.slug = slugify(value, allow_unicode=True)
        super().save(*args, **kwargs)

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
