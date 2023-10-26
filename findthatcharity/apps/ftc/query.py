import copy
from typing import Optional

from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Q
from django.http import Http404, HttpRequest
from elasticsearch_dsl import A

from findthatcharity.apps.ftc.documents import DSEPaginator, OrganisationGroup
from findthatcharity.apps.ftc.models import (
    Organisation,
    OrganisationLocation,
    RelatedOrganisation,
)
from findthatcharity.apps.reconcile.query import RECONCILE_QUERY


def get_organisation(org_id: str) -> Organisation:
    try:
        return Organisation.objects.get(org_id=org_id)
    except Organisation.DoesNotExist or Organisation.MultipleObjectsReturned:
        orgs = list(Organisation.objects.filter(orgIDs__contains=[org_id]))
        if orgs:
            orgs = RelatedOrganisation(orgs)
            return orgs.records[0]
        else:
            raise Http404("No Organisation found.")


def get_linked_organisations(org_id: str) -> RelatedOrganisation:
    related_orgs = list(Organisation.objects.filter(linked_orgs__contains=[org_id]))
    if not related_orgs:
        raise Http404("No Organisation found.")
    return RelatedOrganisation(related_orgs)


def random_query(
    active: bool = False,
    orgtype: Optional[list | str] = None,
    aggregate: bool = False,
    source: Optional[list | str] = None,
) -> dict:
    query = {
        "query": {
            "function_score": {
                "query": {"bool": {"must": []}},
                "boost": "5",
                "random_score": {},
                "boost_mode": "multiply",
            }
        }
    }
    if active:
        query["query"]["function_score"]["query"]["bool"]["must"].append(
            {"match": {"active": True}}
        )

    if orgtype and orgtype != [""]:
        if not isinstance(orgtype, list):
            orgtype = [orgtype]
        query["query"]["function_score"]["query"]["bool"]["must"].append(
            {"terms": {"organisationType": orgtype}}
        )

    if source and source != [""]:
        if not isinstance(source, list):
            source = [source]
        query["query"]["function_score"]["query"]["bool"]["must"].append(
            {"terms": {"sources": source}}
        )

    if aggregate:
        query["aggs"] = {
            "group_by_type": {"terms": {"field": "organisationType", "size": 500}},
            "group_by_source": {"terms": {"field": "sources", "size": 500}},
        }

    return query


class OrganisationSearch:
    def __init__(self, results_per_page: int = 25, **kwargs):
        self.results_per_page: int = results_per_page
        self.term: Optional[str] = None
        self.base_orgtype: Optional[list[str]] = None
        self.other_orgtypes: Optional[list[str]] = None
        self.source: Optional[list[str]] = None
        self.active: Optional[bool] = None
        self.domain: Optional[str] = None
        self.postcode: Optional[str] = None
        self.location: Optional[list[str]] = None

        self.query = None
        self.paginator = None
        self.aggregation = {}

        self.set_criteria(**kwargs)
        self.es_query = copy.deepcopy(RECONCILE_QUERY)

    def set_criteria(
        self,
        term: Optional[str] = None,
        base_orgtype: Optional[list[str] | str] = None,
        other_orgtypes: Optional[list[str] | str] = None,
        source: Optional[list[str] | str] = None,
        active: Optional[bool] = None,
        domain: Optional[str] = None,
        postcode: Optional[str] = None,
        location: Optional[list[str] | str] = None,
    ):
        if term and isinstance(term, str):
            self.term = term

        for t, k in [
            (base_orgtype, "base_orgtype"),
            (other_orgtypes, "other_orgtypes"),
            (source, "source"),
            (location, "location"),
        ]:
            if t:
                if isinstance(t, str) and t != "all":
                    setattr(self, k, t.split("+"))
                elif isinstance(t, list):
                    values = []
                    for v in t:
                        values.extend(v.split("+"))
                    setattr(self, k, values)

        if active is True or active is False:
            self.active = active

        if isinstance(domain, str):
            self.domain = domain

        if isinstance(domain, str):
            self.postcode = postcode

    def set_criteria_from_request(self, request: HttpRequest) -> None:
        if "orgtype" in request.GET and request.GET.get("orgtype") != "all":
            self.set_criteria(other_orgtypes=request.GET.getlist("orgtype"))
        if "source" in request.GET and request.GET.get("source") != "all":
            self.set_criteria(source=request.GET.getlist("source"))
        if "location" in request.GET and request.GET.get("location") != "all":
            self.set_criteria(location=request.GET.getlist("location"))
        if "q" in request.GET:
            self.set_criteria(term=request.GET["q"])
        if request.GET.get("active", "").lower().startswith("t"):
            self.set_criteria(active=True)
        elif request.GET.get("active", "").lower().startswith("f"):
            self.set_criteria(active=False)

    @property
    def orgtypes(self) -> list[str]:
        orgtypes: list[str] = []
        if isinstance(self.base_orgtype, list):
            orgtypes.extend(self.base_orgtype)
        if isinstance(self.other_orgtypes, list):
            orgtypes.extend(self.other_orgtypes)
        return orgtypes

    def run_es(self, with_pagination: bool = False, with_aggregation: bool = False):
        """
        Fetch the reconciliation query and insert the query term
        """

        params = {}

        sort_by = False
        if self.term:
            for param in self.es_query["params"]:
                params[param] = self.term
        else:
            self.es_query["inline"]["query"]["function_score"]["query"]["bool"][
                "must"
            ] = {"match_all": {}}
            # first two functions reference the {{name}} parameter
            self.es_query["inline"]["query"]["function_score"][
                "functions"
            ] = self.es_query["inline"]["query"]["function_score"]["functions"][2:]
            sort_by = "sortname"

        # add postcode
        if self.postcode:
            self.es_query["inline"]["query"]["function_score"]["functions"].append(
                {"filter": {"match": {"postalCode": "{{postcode}}"}}, "weight": 2}
            )
            params["postcode"] = self.postcode

        # add domain searching
        if self.domain:
            self.es_query["inline"]["query"]["function_score"]["functions"].append(
                {"filter": {"term": {"domain": "{{domain}}"}}, "weight": 200000}
            )
            params["domain"] = self.domain

        filter_ = []
        # check for base organisation type
        if self.base_orgtype:
            filter_.append({"terms": {"organisationType": self.base_orgtype}})

        # check for other organisation types
        if self.other_orgtypes:
            filter_.append({"terms": {"organisationType": self.other_orgtypes}})

        # check for source
        if self.source:
            filter_.append({"terms": {"source": self.source}})

        # check for location
        if self.location:
            filter_.append({"terms": {"locations": self.location}})

        # check for active or inactive organisations
        if self.active is True:
            filter_.append({"match": {"active": True}})
        elif self.active is False:
            filter_.append({"match": {"active": False}})

        if filter_:
            self.es_query["inline"]["query"]["function_score"]["query"]["bool"][
                "filter"
            ] = filter_

        q = (
            OrganisationGroup.search()
            .from_dict(self.es_query["inline"])
            .params(track_total_hits=True)
            .index(OrganisationGroup._default_index())
        )
        if sort_by:
            q = q.sort(sort_by)

        if with_aggregation:
            by_source = A("terms", field="source", size=150)
            by_orgtype = A("terms", field="organisationType", size=150)
            by_active = A("terms", field="active", size=150)
            by_location = A("terms", field="locations", size=1000)
            q.aggs.bucket("by_source", by_source)
            q.aggs.bucket("by_orgtype", by_orgtype)
            q.aggs.bucket("by_active", by_active)
            q.aggs.bucket("by_location", by_location)

        self.query = q.execute(params=params)
        if with_pagination:
            self.paginator = DSEPaginator(q, self.results_per_page, params=params)

        if with_aggregation:
            self.aggregation["by_source"] = [
                {"source": b["key"], "records": b["doc_count"]}
                for b in self.query.aggregations["by_source"]["buckets"]
            ]
            self.aggregation["by_orgtype"] = [
                {"orgtype": b["key"], "records": b["doc_count"]}
                for b in self.query.aggregations["by_orgtype"]["buckets"]
            ]
            self.aggregation["by_location"] = {
                b["key"]: b["doc_count"]
                for b in self.query.aggregations["by_location"]["buckets"]
            }
            self.aggregation["by_active"] = {
                "active": 0,
                "inactive": 0,
            }
            for b in self.query.aggregations["by_active"]["buckets"]:
                if b["key"]:
                    self.aggregation["by_active"]["active"] = b["doc_count"]
                else:
                    self.aggregation["by_active"]["inactive"] = b["doc_count"]

    def run_db(self, with_pagination=False, with_aggregation=False):
        db_filter = []
        if self.base_orgtype:
            db_filter.append(Q(organisationType__contains=self.base_orgtype))
        if self.other_orgtypes:
            db_filter.append(Q(organisationType__contains=self.other_orgtypes))
        if self.source:
            db_filter.append(Q(source__id__in=self.source))
        if self.term:
            db_filter.append(Q(name__search=self.term))
        if self.active is True or self.active is False:
            db_filter.append(Q(active=self.active))

        # check for location
        if self.location:
            location_filter = OrganisationLocation.objects.filter(
                Q(geo_iso__in=self.location)
                | Q(geo_laua__in=self.location)
                | Q(geo_rgn__in=self.location)
                | Q(geo_ctry__in=self.location)
                | Q(geoCode__in=self.location)
            ).values("org_id")
            db_filter.append(Q(org_id__in=location_filter))

        self.query = Organisation.objects.filter(*db_filter)

        if with_pagination:
            self.paginator = Paginator(
                self.query.order_by("name"), self.results_per_page
            )

        if with_aggregation:
            self.aggregation["by_orgtype"] = (
                self.query.annotate(
                    orgtype=Func(F("organisationType"), function="unnest")
                )
                .values("orgtype")
                .annotate(records=Count("*"))
                .order_by("-records")
            )

            self.aggregation["by_source"] = (
                self.query.values("source")
                .annotate(records=Count("source"))
                .order_by("-records")
            )
