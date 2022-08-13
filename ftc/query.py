from django.contrib.postgres.search import SearchQuery, SearchRank
from django.core.paginator import Paginator
from django.db.models import Count, F, Func, Q
from django.shortcuts import Http404

from ftc.models import Organisation, RelatedOrganisation, OrganisationGroup


def get_organisation(org_id):
    try:
        return Organisation.objects.get(org_id=org_id)
    except Organisation.DoesNotExist or Organisation.MultipleObjectsReturned:
        orgs = list(Organisation.objects.filter(orgIDs__contains=[org_id]))
        if orgs:
            orgs = RelatedOrganisation(orgs)
            return orgs.records[0]
        else:
            raise Http404("No Organisation found.")


def get_linked_organisations(org_id):
    related_orgs = list(Organisation.objects.filter(linked_orgs__contains=[org_id]))
    if not related_orgs:
        raise Http404("No Organisation found.")
    return RelatedOrganisation(related_orgs)


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
        self.location = None

        self.query = None
        self.paginator = None
        self.aggregation = {}

        self.set_criteria(**kwargs)

    def set_criteria(
        self,
        term=None,
        base_orgtype=None,
        other_orgtypes=None,
        source=None,
        active=None,
        domain=None,
        postcode=None,
        location=None,
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
                        if isinstance(v, str):
                            values.extend(v.split("+"))
                        else:
                            values.append(v)
                    setattr(self, k, values)

        if active is True or active is False:
            self.active = active

        if isinstance(domain, str):
            self.domain = domain

        if isinstance(domain, str):
            self.postcode = postcode

    def set_criteria_from_request(self, request):
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
    def orgtypes(self):
        orgtypes = []
        if isinstance(self.base_orgtype, list):
            orgtypes.extend(self.base_orgtype)
        if isinstance(self.other_orgtypes, list):
            orgtypes.extend(self.other_orgtypes)
        return orgtypes

    def run_db(self, with_pagination=False, with_aggregation=False):
        db_filter = []
        search_query = None
        order_by = "name"
        if self.base_orgtype:
            db_filter.append(Q(organisationType__contains=self.base_orgtype))
        if self.other_orgtypes:
            db_filter.append(Q(organisationType__contains=self.other_orgtypes))
        if self.source:
            db_filter.append(Q(source__contains=self.source))
        if self.term:
            search_query = SearchQuery(self.term)
            db_filter.append(Q(search_vector=search_query))
        if self.active is True or self.active is False:
            db_filter.append(Q(active=self.active))

        # check for location
        if self.location:
            db_filter.append(Q(locations__contains=self.location))

        self.query = OrganisationGroup.objects.filter(*db_filter)

        if search_query:
            search_rank = SearchRank(F("search_vector"), search_query)
            self.query = self.query.annotate(
                rank=search_rank * F("search_scale"),
            )
            order_by = "-rank"

        if with_pagination:
            self.paginator = Paginator(
                self.query.order_by(order_by), self.results_per_page
            )
        else:
            self.paginator = Paginator(self.query.order_by(order_by), 1)

        if with_aggregation:
            self.aggregation["by_orgtype"] = list(
                self.query.annotate(
                    orgtype=Func(F("organisationType"), function="unnest")
                )
                .values("orgtype")
                .annotate(records=Count("*"))
                .order_by("-records")
            )

            self.aggregation["by_source"] = [
                {"source": r["by_source"], "records": r["records"]}
                for r in self.query.annotate(
                    by_source=Func(F("source"), function="unnest")
                )
                .values("by_source")
                .annotate(records=Count("source"))
                .order_by("-records")
            ]

            self.aggregation["by_location"] = {
                r["location"]: r["records"]
                for r in self.query.annotate(
                    location=Func(F("locations"), function="unnest")
                )
                .values("location")
                .annotate(records=Count("locations"))
                .order_by("-records")
            }

            self.aggregation["by_active"] = {
                "active": 0,
                "inactive": 0,
            }
            for record in (
                self.query.values("active")
                .annotate(records=Count("active"))
                .order_by("-records")
            ):
                if record["active"]:
                    self.aggregation["by_active"]["active"] = record["records"]
                else:
                    self.aggregation["by_active"]["inactive"] = record["records"]
