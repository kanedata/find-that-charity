from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django_better_admin_arrayfield.models.fields import ArrayField

from findthatcharity.utils import get_domain, normalise_name
from ftc.models.organisation import Organisation
from ftc.models.orgid import OrgidField
from ftc.models.related_organisation import RelatedOrganisation


class OrganisationGroup(models.Model):
    org_id = OrgidField(
        db_index=True, verbose_name="Organisation Identifier", primary_key=True
    )
    orgIDs = ArrayField(
        OrgidField(blank=True),
        verbose_name="Other organisation identifiers",
    )
    name = models.CharField(max_length=255, db_index=True, verbose_name="Name")
    sortname = models.CharField(max_length=255, db_index=True, verbose_name="Sort Name")
    alternateName = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Other names",
    )
    postalCode = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Postcode", db_index=True
    )
    domain = ArrayField(
        models.CharField(max_length=255, blank=True),
        null=True,
        blank=True,
        verbose_name="Website domain",
    )
    active = models.BooleanField(null=True, blank=True, verbose_name="Active")
    organisationType = models.ManyToManyField(
        "OrganisationType",
        verbose_name="Other organisation types",
    )
    organisationTypePrimary = models.ForeignKey(
        "OrganisationType",
        on_delete=models.DO_NOTHING,
        related_name="organisation_groups",
        verbose_name="Primary organisation type",
    )
    source = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Data source",
    )
    locations = ArrayField(
        models.CharField(max_length=255, blank=True),
        blank=True,
        null=True,
        verbose_name="Locations",
    )
    search_vector = SearchVectorField(null=True)
    search_scale = models.FloatField(null=False, default=1, db_index=True)

    class Meta:
        indexes = [
            GinIndex(fields=["orgIDs"]),
            GinIndex(fields=["alternateName"]),
            # GinIndex(fields=["organisationType"]),
            GinIndex(fields=["locations"]),
            GinIndex(fields=["search_vector"]),
        ]

    @classmethod
    def from_orgid(cls, org_id):
        orgs = Organisation.objects.filter(linked_orgs__contains=[org_id])
        return cls.from_orgs(orgs)

    @classmethod
    def from_orgs(cls, orgs):
        org = RelatedOrganisation(orgs)
        org_group = dict(
            org_id=org.org_id,
            orgIDs=org.orgIDs,
            name=org.name,
            sortname=normalise_name(org.name),
            alternateName=org.alternateName,
            postalCode=org.postalCode,
            domain=list(
                filter(
                    lambda item: item is not None,
                    [get_domain(link) for link in org.get_all("url")],
                )
            ),
            active=org.active,
            organisationTypePrimary_id=org.organisationTypePrimary_id,
            source=org.source_ids,
            locations=org.geocodes,
            search_scale=org.search_scale(),
        )
        return cls(**org_group), org

    def __str__(self):
        return "%s %s" % (self.organisationTypePrimary.title, self.org_id)
