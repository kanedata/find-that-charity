from itertools import groupby
from math import ceil

import tqdm
from charity_django.companies.models import Company
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.utils.translation import gettext_lazy as _
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.search import Search
from elasticsearch.helpers import bulk
from elasticsearch_dsl import analyzer, token_filter
from elasticsearch_dsl.connections import get_connection

from findthatcharity.utils import get_domain, normalise_name
from ftc.models import Organisation, RelatedOrganisation


class SearchWithTemplate(Search):
    def execute(self, ignore_cache=False, params=None):
        """
        Execute the search and return an instance of ``Response`` wrapping all
        the data.
        :arg ignore_cache: if set to ``True``, consecutive calls will hit
            ES, while cached result will be ignored. Defaults to `False`
        """
        if ignore_cache or not hasattr(self, "_response"):
            es = get_connection(self._using)

            if params:
                search_body = es.render_search_template(
                    body={"source": self.to_dict(), "params": params},
                )["template_output"]
            else:
                search_body = self.to_dict()
            self._response = self._response_class(
                self, es.search(index=self._index, body=search_body, **self._params)
            )
        return self._response


class DSEPaginator(Paginator):
    """
    Override Django's built-in Paginator class to take in a count/total number of items;
    Elasticsearch provides the total as a part of the query results, so we can minimize hits.
    """

    def __init__(self, *args, params=None, **kwargs):
        super(DSEPaginator, self).__init__(*args, **kwargs)
        self._params = params
        self.count = None
        self.num_pages = None

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            if isinstance(number, float) and not number.is_integer():
                raise ValueError
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(_("That page number is not an integer"))
        if number < 1:
            raise EmptyPage(_("That page number is less than 1"))
        return number

    def page(self, number):
        """Return a Page object for the given 1-based page number."""
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)

    def _get_page(self, object_list, number, paginator):
        self.result = object_list.execute(params=self._params)
        if isinstance(self.result.hits.total, int):
            self.count = self.result.hits.total
        else:
            self.count = int(self.result.hits.total.value)

        if self.count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self.count - self.orphans)
        self.num_pages = ceil(hits / self.per_page)
        return Page(self.result, number, self)


name_analyzer = analyzer(
    "ftc_name_analyzer",
    tokenizer="standard",
    filter=[
        token_filter(
            "ftc_english_possesive_stemmer", "stemmer", language="possessive_english"
        ),
        "lowercase",
        token_filter(
            "ftc_synonym",
            "synonym",
            synonyms=[
                "c.i.c. => cic",
                "c i c => cic",
                "c.i.c => cic",
                "community interest company => cic",
                "s.c.i.o. => scio",
                "s c i o => scio",
                "s.c.i.o => scio",
                "scottish charitable incorporated organisation => scio",
                "c.i.o. => cio",
                "c i o => cio",
                "c.i.o => cio",
                "charitable incorporated organisation => cio",
                "n.h.s. => nhs",
                "n h s => nhs",
                "n.h.s => nhs",
                "national health service => nhs",
                "ltd => limited",
                "ltd. => limited",
                "u.k. => uk",
                "u.k => uk",
                "united kingdom => uk",
                "pre-school => preschool",
                "pre school => preschool",
            ],
        ),
        # token_filter(
        #     "ftc_shingles",
        #     "shingle",
        #     min_shingle_size=2,
        #     max_shingle_size=2,
        #     token_separator="",
        #     filler_token="",
        # ),
        token_filter("ftc_english_stop", "stop", stopwords="_english_"),
        token_filter(
            "ftc_english_keyword_marker",
            "keyword_marker",
            keywords=["limited", "nhs", "cio", "scio", "cic", "uk"],
        ),
        "kstem",
        # "remove_duplicates",
        # token_filter("ftc_english_stemmer", "stemmer", language="english"),
    ],
    char_filter=["html_strip"],
)


@registry.register_document
class OrganisationGroup(Document):
    org_id = fields.KeywordField()
    complete_names = fields.CompletionField(
        contexts=[
            {"name": "organisationType", "type": "category", "path": "organisationType"}
        ]
    )
    orgIDs = fields.KeywordField()
    ids = fields.KeywordField()
    name = fields.TextField(analyzer=name_analyzer)  # Indexed from the model
    sortname = fields.KeywordField()
    alternateName = fields.TextField(analyzer=name_analyzer)
    # postalCode = fields.KeywordField()  # Indexed from the model
    domain = fields.KeywordField()
    # active = fields.BooleanField()  # Indexed from the model
    organisationType = fields.KeywordField()
    organisationTypePrimary = fields.KeywordField()
    source = fields.KeywordField()
    locations = fields.KeywordField()
    search_scale = fields.FloatField()
    hq_ward = fields.KeywordField()
    hq_localauthority = fields.KeywordField()
    hq_region = fields.KeywordField()
    hq_country = fields.KeywordField()

    @classmethod
    def search(cls, using=None, index=None):
        return SearchWithTemplate(
            using=cls._get_using(using),
            index=cls._default_index(index),
            doc_type=[cls],
            model=cls.django.model,
        )

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
            search_scale=org.search_scale,
        )
        return cls(**org_group), org

    class Index:
        # Name of the Elasticsearch index
        name = "ftc_organisation"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    def prepare_complete_names(self, instance):
        words = set()
        for n in instance.alternateName + [instance.name]:
            if n:
                w = n.split()
                words.update([" ".join(w[r:]) for r in range(len(w))])
        return list(words)

    def _prepare_action(self, object_instance, action):
        result = super(OrganisationGroup, self)._prepare_action(object_instance, action)
        result["_id"] = object_instance.org_id
        return result

    def prepare_org_id(self, instance):
        return str(instance.org_id)

    def prepare_orgIDs(self, instance):
        return instance.orgIDs

    def prepare_ids(self, instance):
        return [o.id for o in instance.orgIDs] + [
            o.id.lstrip("0") for o in instance.orgIDs if o.id.lstrip("0") != o.id
        ]

    def prepare_alternateName(self, instance):
        return instance.alternateName

    def prepare_sortname(self, instance):
        return normalise_name(instance.name)

    def prepare_domain(self, instance):
        return list(
            set(
                filter(
                    lambda item: item is not None,
                    [get_domain(link) for link in instance.get_all("url")],
                )
            )
        )

    def prepare_organisationType(self, instance):
        return list(instance.get_all("organisationType"))

    def prepare_organisationTypePrimary(self, instance):
        return instance.organisationTypePrimary_id

    def prepare_locations(self, instance):
        return instance.geocodes

    def prepare_hq_ward(self, instance):
        return instance.hq_region("ward")

    def prepare_hq_localauthority(self, instance):
        return instance.hq_region("laua")

    def prepare_hq_region(self, instance):
        return instance.hq_region("rgn")

    def prepare_hq_country(self, instance):
        return instance.hq_region("ctry")

    def prepare_search_scale(self, instance):
        return instance.search_scale

    def prepare_source(self, instance):
        return list(instance.get_all("source_id"))

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        return self.django.model.objects.filter(linked_orgs__isnull=False).order_by(
            "linked_orgs"
        )

    def get_indexing_queryset(self):
        """
        Build queryset (iterator) for use by indexing.
        """
        qs = self.get_queryset()
        for k, orgs in groupby(
            tqdm.tqdm(
                qs.iterator(), total=qs.count(), position=0, smoothing=0.1, leave=True
            ),
            key=lambda o: o.linked_orgs,
        ):
            yield RelatedOrganisation(orgs)

    def bulk(self, actions, **kwargs):
        if self.django.queryset_pagination and "chunk_size" not in kwargs:
            kwargs["chunk_size"] = self.django.queryset_pagination
        return bulk(client=self._get_connection(), actions=actions, **kwargs)

    class Django:
        model = Organisation  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            # "name",
            "postalCode",
            "dateModified",
            "active",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        queryset_pagination = 3000

    def get_related_orgs(self):
        return Organisation.objects.filter(org_id__in=self.orgIDs)


@registry.register_document
class CompanyDocument(Document):
    CompanyName = fields.TextField(analyzer=name_analyzer)
    CompanyNumber = fields.KeywordField(attr="CompanyNumber")
    CompanyStatus = fields.KeywordField(attr="CompanyStatus")
    RegAddress_PostCode = fields.KeywordField(attr="RegAddress_PostCode")
    CompanyCategory = fields.KeywordField(attr="CompanyCategory")
    PreviousNames = fields.TextField(analyzer=name_analyzer)
    RegAddress_Ward = fields.KeywordField(attr="RegAddress_Ward")
    RegAddress_LocalAuthority = fields.KeywordField(attr="RegAddress_LocalAuthority")
    RegAddress_Region = fields.KeywordField(attr="RegAddress_Region")
    RegAddress_Country = fields.KeywordField(attr="RegAddress_Country")

    @classmethod
    def search(cls, using=None, index=None):
        return SearchWithTemplate(
            using=cls._get_using(using),
            index=cls._default_index(index),
            doc_type=[cls],
            model=cls.django.model,
        )

    def bulk(self, actions, **kwargs):
        if self.django.queryset_pagination and "chunk_size" not in kwargs:
            kwargs["chunk_size"] = self.django.queryset_pagination
        return bulk(client=self._get_connection(), actions=actions, **kwargs)

    def get_queryset(self):
        """
        Return the queryset that should be indexed by this doc type.
        """
        return self.django.model.objects.raw(
            """
            WITH names AS (
                SELECT "CompanyNumber",
                    json_agg("CompanyName") AS "names"
                FROM "companies_previousname"
                GROUP BY "CompanyNumber"
            )
            SELECT c."CompanyNumber",
                c."CompanyName",
                c."CompanyStatus",
                c."RegAddress_PostCode",
                c."CompanyCategory",
                names.names AS "PreviousNames",
                p.ward AS "RegAddress_Ward",
                p.laua AS "RegAddress_LocalAuthority",
                p.rgn AS "RegAddress_Region",
                p.ctry AS "RegAddress_Country"
            FROM "companies_company" c
                LEFT OUTER JOIN names
                    ON c."CompanyNumber" = names."CompanyNumber"
                LEFT OUTER JOIN geo_postcode p
                    ON c."RegAddress_PostCode" = p.pcds
            """
        )

    def get_indexing_queryset(self):
        return self.get_queryset()

    class Index:
        # Name of the Elasticsearch index
        name = "companies"
        # See Elasticsearch Indices API reference for available settings
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Company  # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            # "CompanyName",
        ]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        queryset_pagination = 20000
