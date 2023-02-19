import urllib.parse
from typing import List, Literal, Optional, Union

from django.http import Http404, HttpResponse
from django.shortcuts import reverse
from ninja_extra import api_controller, http_get, http_post

from findthatcharity.jinja2 import get_orgtypes
from ftc.documents import OrganisationGroup
from ftc.models import Organisation, OrganisationType, Vocabulary
from ftc.views import get_org_by_id
from reconcile.companies import COMPANY_RECON_TYPE
from reconcile.companies import do_reconcile_query as do_companies_reconcile_query
from reconcile.query import do_extend_query, do_reconcile_query

from .schema import (
    DataExtensionPropertyProposalResponse,
    DataExtensionQuery,
    DataExtensionQueryResponse,
    ReconciliationQueryBatch,
    ReconciliationResultBatch,
    ServiceSpec,
    SuggestResponse,
)


def get_orgtypes_from_str(
    orgtype: Optional[Union[List[str], str]] = None
) -> List[OrganisationType]:
    if orgtype == "all":
        return []
    if isinstance(orgtype, str):
        return [OrganisationType.objects.get(slug=o) for o in orgtype.split("+")]
    if isinstance(orgtype, list):
        return [OrganisationType.objects.get(slug=o) for o in orgtype]
    return []


@api_controller(
    "/reconcile",
    tags=["Reconciliation (against all organisations)"],
)
class API:
    def _get_service_spec(
        self, request, orgtypes: Optional[Union[List[str], Literal["all"]]] = None
    ):
        if not orgtypes or orgtypes == "all":
            defaultTypes = [{"id": "/Organization", "name": "Organisation"}]
        elif isinstance(orgtypes, list):
            defaultTypes = [{"id": o.slug, "name": o.title} for o in orgtypes]

        return {
            "versions": ["0.2"],
            "name": "Find that Charity Reconciliation API",
            "identifierSpace": "http://org-id.guide",
            "schemaSpace": "https://schema.org",
            "view": {
                "url": urllib.parse.unquote(
                    request.build_absolute_uri(
                        reverse("orgid_html", kwargs={"org_id": "{{id}}"})
                    )
                )
            },
            "preview": {
                "width": 430,
                "height": 300,
            },
            "defaultTypes": defaultTypes,
            "extend": {
                "propose_properties": True,
                "property_settings": [],
            },
            "suggest": {
                "entity": True,
            },
        }

    def _reconcile(
        self, request, body: ReconciliationQueryBatch, orgtypes: List[OrganisationType]
    ):
        return {
            "results": [
                do_reconcile_query(
                    query.query,
                    type=query.type,
                    limit=query.limit,
                    properties=query.properties,
                    type_strict=query.type_strict,
                    result_key="candidates",
                    orgtypes=orgtypes,
                )
                for query in body.queries
            ]
        }

    def _preview(
        self,
        request,
        id: str,
        orgtypes: Optional[Union[List[str], Literal["all"]]] = None,
    ):
        return get_org_by_id(request, id, preview=True)

    def _suggest_entity(
        self,
        request,
        prefix: str,
        cursor: int = 0,
        orgtypes: Optional[Union[List[str], Literal["all"]]] = None,
    ):
        SUGGEST_NAME = "name_complete"

        # cursor = request.GET.get("cursor")
        if not prefix:
            raise Http404("Prefix must be supplied")
        q = OrganisationGroup.search()

        orgtype = []
        if isinstance(orgtypes, list):
            for o in orgtypes:
                if o == "all":
                    continue
                orgtype.append(o.slug)

        completion = {"field": "complete_names", "fuzzy": {"fuzziness": 1}}
        if orgtype:
            completion["contexts"] = dict(organisationType=orgtype)
        else:
            all_orgtypes = get_orgtypes()
            completion["contexts"] = dict(
                organisationType=[o for o in all_orgtypes.keys()]
            )

        q = q.suggest(SUGGEST_NAME, prefix, completion=completion).source(
            ["org_id", "name", "organisationType"]
        )
        result = q.execute()

        return {
            "result": [
                {
                    "id": r["_source"]["org_id"],
                    "name": r["_source"]["name"],
                    "notable": list(r["_source"]["organisationType"]),
                }
                for r in result.suggest[SUGGEST_NAME][0]["options"]
            ]
        }

    def _propose_properties(self, request, type_, limit=500):
        if type_ != "Organization":
            raise Http404("type must be Organization")

        organisation_properties = Organisation.get_fields_as_properties()

        vocabulary_properties = [
            {"id": "vocab-" + v.slug, "name": v.title, "group": "Vocabulary"}
            for v in Vocabulary.objects.all()
            if v.entries.count() > 0
        ]

        ccew_properties = [
            {
                "id": "ccew-parta-total_gross_expenditure",
                "name": "Total Expenditure",
                "group": "Charity",
            },
            {
                "id": "ccew-partb-count_employees",
                "name": "Number of staff",
                "group": "Charity",
            },
            {
                "id": "ccew-partb-expenditure_charitable_expenditure",
                "name": "Charitable expenditure",
                "group": "Charity",
            },
            {
                "id": "ccew-partb-expenditure_grants_institution",
                "name": "Grantmaking expenditure",
                "group": "Charity",
            },
            {
                "id": "ccew-gd-charitable_objects",
                "name": "Objects",
                "group": "Charity",
            },
            {
                "id": "ccew-aoo-geographic_area_description",
                "name": "Area of Operation",
                "group": "Charity",
            },
        ]

        return {
            "limit": limit,
            "type": type_,
            "properties": organisation_properties
            + vocabulary_properties
            + ccew_properties,
        }

    def _data_extension(self, request, body: DataExtensionQuery):
        def convert_value(v):
            if isinstance(v, dict):
                return v
            elif isinstance(v, list):
                return [convert_value(vv)[0] for vv in v]
            elif isinstance(v, str):
                return [{"str": v}]
            elif isinstance(v, int):
                return [{"int": v}]
            elif isinstance(v, float):
                return [{"float": v}]
            elif isinstance(v, bool):
                return [{"bool": v}]
            else:
                return [{"str": str(v)}]

        result = do_extend_query(
            ids=body.ids,
            properties=[p.__dict__ for p in body.properties],
        )
        return {
            "meta": result["meta"],
            "rows": [
                {
                    "id": row_id,
                    "properties": [
                        {"id": k, "values": convert_value(v)} for k, v in row.items()
                    ],
                }
                for row_id, row in result["rows"].items()
            ],
        }

    @http_get(
        "",
        response={200: ServiceSpec},
        exclude_none=True,
        summary="Service specification for reconciling against any nonprofit organisation",
        description="Get the service specification for reconciling against any nonprofit organisation",
    )
    def get_service_spec(self, request):
        return self._get_service_spec(request, orgtypes="all")

    @http_post(
        "",
        response={200: ReconciliationResultBatch},
        exclude_none=True,
        summary="Reconciliation endpoint for reconciling against any nonprofit organisation",
        description="Reconciling queries against any nonprofit organisation.",
    )
    def reconcile(self, request, body: ReconciliationQueryBatch):
        return self._reconcile(request, body)

    @http_get("/preview")
    def preview(self, request, id: str, response: HttpResponse):
        return self._preview(request, id, response)

    @http_get("/suggest/entity", response={200: SuggestResponse}, exclude_none=True)
    def suggest_entity(self, request, prefix: str, cursor: int = 0):
        return self._suggest_entity(request, prefix, cursor)

    @http_get(
        "/extend/propose",
        response={200: DataExtensionPropertyProposalResponse},
        exclude_none=True,
    )
    def propose_properties(self, request, type: str, limit: int = 500):
        return self._propose_properties(request, type_=type, limit=limit)

    @http_post(
        "/extend",
        response={200: DataExtensionQueryResponse},
        exclude_none=True,
    )
    def data_extension(self, request, body: DataExtensionQuery):
        return self._data_extension(request, body)

    @http_get(
        "/company",
        response={200: ServiceSpec},
        exclude_none=True,
        tags=["Reconciliation (against registered companies)"],
    )
    def get_company_service_spec(self, request):
        return {
            "versions": ["0.2"],
            "name": "Find that Charity Company Reconciliation API",
            "identifierSpace": "http://org-id.guide",
            "schemaSpace": "https://schema.org",
            "view": {
                "url": urllib.parse.unquote(
                    request.build_absolute_uri(
                        reverse("company_detail", kwargs={"company_number": "{{id}}"})
                    )
                )
            },
            # "preview": {
            #     "width": 430,
            #     "height": 300,
            # },
            "defaultTypes": [COMPANY_RECON_TYPE],
        }

    @http_post(
        "/company",
        response={200: ReconciliationResultBatch},
        exclude_none=True,
        tags=["Reconciliation (against registered companies)"],
    )
    def company_reconcile(self, request, body: ReconciliationQueryBatch):
        return {
            "results": [
                do_companies_reconcile_query(
                    query.query,
                    type=query.type,
                    limit=query.limit,
                    properties=query.properties,
                    type_strict=query.type_strict,
                    result_key="candidates",
                )
                for query in body.queries
            ]
        }

    @http_get(
        "/{orgtype}",
        response={200: ServiceSpec},
        exclude_none=True,
        tags=["Reconciliation (against specific type of organisation)"],
        summary="Service specification for reconciling against a specific type of organisation",
        description="Get the service specification for reconciling against a specific type of organisation",
    )
    def orgtype_get_service_spec(self, request, orgtype: str):
        return self._get_service_spec(request, orgtypes=get_orgtypes_from_str(orgtype))

    @http_post(
        "/{orgtype}",
        response={200: ReconciliationResultBatch},
        exclude_none=True,
        tags=["Reconciliation (against specific type of organisation)"],
        summary="Reconciliation endpoint for reconciling against a specific type of organisation",
        description="Reconciling queries against a specific type of organisation. You can specify multiple types of organisation by separating them with a '+'.",
    )
    def orgtype_reconcile(self, request, orgtype: str, body: ReconciliationQueryBatch):
        return self._reconcile(request, body, orgtypes=get_orgtypes_from_str(orgtype))

    @http_get(
        "/{orgtype}/preview",
        tags=["Reconciliation (against specific type of organisation)"],
        summary="HTML preview of an organisation",
    )
    def orgtype_preview(self, request, orgtype: str, id: str, response: HttpResponse):
        return self._preview(request, id, response)

    @http_get(
        "/{orgtype}/suggest/entity",
        response={200: SuggestResponse},
        exclude_none=True,
        tags=["Reconciliation (against specific type of organisation)"],
    )
    def orgtype_suggest_entity(
        self, request, orgtype: str, prefix: str, cursor: int = 0
    ):
        return self._suggest_entity(
            request, prefix, cursor, orgtypes=get_orgtypes_from_str(orgtype)
        )

    @http_get(
        "/{orgtype}/extend/propose",
        response={200: DataExtensionPropertyProposalResponse},
        exclude_none=True,
        tags=["Reconciliation (against specific type of organisation)"],
    )
    def orgtype_propose_properties(
        self, request, orgtype: str, type: str, limit: int = 500
    ):
        return self._propose_properties(request, type_=type, limit=limit)

    @http_post(
        "/{orgtype}/extend",
        response={200: DataExtensionQueryResponse},
        exclude_none=True,
        tags=["Reconciliation (against specific type of organisation)"],
    )
    def orgtype_data_extension(self, request, orgtype: str, body: DataExtensionQuery):
        return self._data_extension(request, body)
