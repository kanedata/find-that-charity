import copy

from django.core.paginator import Paginator
from django.db.models import Count, F, Func
from elasticsearch_dsl import A

from ftc.documents import DSEPaginator, FullOrganisation
from ftc.models import Organisation
from reconcile.query import RECONCILE_QUERY


def random_query(active=False, orgtype=None, aggregate=False, source=None):
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
    def __init__(self, results_per_page=25, **kwargs):
        self.results_per_page = results_per_page
        self.term = None
        self.base_orgtype = None
        self.other_orgtypes = None
        self.source = None
        self.active = None
        self.domain = None
        self.postcode = None

        self.query = None
        self.paginator = None
        self.aggregation = {}

        self.set_criteria(**kwargs)
        self.es_query = copy.deepcopy(RECONCILE_QUERY)

    def set_criteria(
        self,
        term=None,
        base_orgtype=None,
        other_orgtypes=None,
        source=None,
        active=None,
        domain=None,
        postcode=None,
    ):
        if term and isinstance(term, str):
            self.term = term

        for t, k in [
            (base_orgtype, "base_orgtype"),
            (other_orgtypes, "other_orgtypes"),
            (source, "source"),
        ]:
            if t:
                if isinstance(t, str) and t != "all":
                    setattr(self, k, t.split("+"))
                elif isinstance(t, list):
                    setattr(self, k, t)

        if active is True or active is False:
            self.active = active

        if isinstance(domain, str):
            self.domain = domain

        if isinstance(domain, str):
            self.postcode = postcode

    def set_criteria_from_request(self, request):
        pass

    def run_es(self, with_pagination=False, with_aggregation=False):
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

        if filter_:
            self.es_query["inline"]["query"]["function_score"]["query"]["bool"][
                "filter"
            ] = filter_

        q = (
            FullOrganisation.search()
            .from_dict(self.es_query["inline"])
            .params(track_total_hits=True)
        )
        if sort_by:
            q = q.sort(sort_by)

        if with_aggregation:
            by_source = A("terms", field="source")
            by_orgtype = A("terms", field="organisationType")
            q.aggs.bucket("by_source", by_source)
            q.aggs.bucket("by_orgtype", by_orgtype)

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

    def run_db(self, with_pagination=False, with_aggregation=False):
        db_filter = {}
        if self.base_orgtype:
            db_filter["organisationType__contains"] = self.base_orgtype
        if self.source:
            db_filter["source__id__in"] = self.source
        if self.term:
            db_filter["name__search"] = self.term
        if self.active is True or self.active is False:
            db_filter["active"] = self.active

        self.query = Organisation.objects.filter(
            **{k: v for k, v in db_filter.items() if v}
        )

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
