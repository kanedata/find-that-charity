import urllib.parse
from typing import Dict, List, Literal, Optional, Union

from django.db.models import Q
from django.http import Http404
from django.shortcuts import reverse

from findthatcharity.jinja2 import get_orgtypes
from ftc.documents import OrganisationGroup
from ftc.models import Organisation, OrganisationType, Vocabulary
from ftc.views import get_org_by_id
from reconcile.query import do_extend_query, do_reconcile_query
from reconcile.utils import convert_value

from .schema import (
    DataExtensionQuery,
    ReconciliationCandidate,
    ReconciliationQueryBatch,
)


class Reconcile:
    name = "Find that Charity Reconciliation API"
    view_url = "orgid_html"
    view_url_args = {"org_id": "{{id}}"}
    suggest_entity = True
    suggest_type = True
    extend = True
    preview = True

    def reconcile_query(self, *args, **kwargs):
        return do_reconcile_query(*args, **kwargs)

    def _get_orgtypes_from_str(
        self, orgtype: Optional[Union[List[str], str]] = None
    ) -> List[OrganisationType]:
        if orgtype == "all":
            return []
        if isinstance(orgtype, str):
            return [OrganisationType.objects.get(slug=o) for o in orgtype.split("+")]
        if isinstance(orgtype, list):
            orgtypes = []
            for o in orgtype:
                if o == "all":
                    continue
                if isinstance(o, str):
                    orgtypes.append(OrganisationType.objects.get(slug=o))
                elif isinstance(o, OrganisationType):
                    orgtypes.append(o)
            return orgtypes
        return []

    def get_service_spec(
        self,
        request,
        orgtypes: Optional[Union[List[str], Literal["all"]]] = None,
        defaultTypes: Optional[List[dict]] = None,
    ):
        if orgtypes:
            orgtypes = self._get_orgtypes_from_str(orgtypes)
        if not defaultTypes:
            if not orgtypes or orgtypes == "all":
                defaultTypes = [
                    {"id": "registered-charity", "name": "Registered Charity"}
                ]
            elif isinstance(orgtypes, list):
                defaultTypes = [{"id": o.slug, "name": o.title} for o in orgtypes]

        request_path = request.build_absolute_uri(request.path).rstrip("/")

        spec = {
            "versions": ["0.2"],
            "name": self.name,
            "identifierSpace": "http://org-id.guide",
            "schemaSpace": "https://schema.org",
            "view": {
                "url": urllib.parse.unquote(
                    request.build_absolute_uri(
                        reverse(self.view_url, kwargs=self.view_url_args)
                    )
                )
            },
            "defaultTypes": defaultTypes,
        }
        if self.preview:
            spec["preview"] = {
                "url": request_path + "/preview?id={{id}}",
                "width": 430,
                "height": 300,
            }
        if self.extend:
            spec["extend"] = {
                "propose_properties": {
                    "service_url": request_path,
                    "service_path": "/extend/propose",
                },
                "property_settings": [],
            }
        if self.suggest_entity or self.suggest_type:
            spec["suggest"] = {}
            if self.suggest_entity:
                spec["suggest"]["entity"] = {
                    "service_url": request_path,
                    "service_path": "/suggest/entity",
                }
            if self.suggest_type:
                spec["suggest"]["type"] = {
                    "service_url": request_path,
                    "service_path": "/suggest/type",
                }
        return spec

    def reconcile(
        self,
        request,
        body: ReconciliationQueryBatch,
        orgtypes: List[OrganisationType] | List[str] | Literal["all"] = None,
    ) -> Dict[str, List[ReconciliationCandidate]]:
        orgtypes = self._get_orgtypes_from_str(orgtypes)
        results = {}
        for key, query in body.queries.items():
            results[key] = self.reconcile_query(
                query.query,
                type_=self._get_orgtypes_from_str(query.type),
                limit=query.limit,
                properties=query.properties,
                type_strict=query.type_strict,
                result_key="result",
                orgtypes=orgtypes,
            )
        return results

    def preview_view(
        self,
        request,
        id: str,
        orgtypes: Optional[Union[List[str], Literal["all"]]] = None,
    ):
        return get_org_by_id(request, id, preview=True)

    def suggest_entity(
        self,
        request,
        prefix: str,
        cursor: int = 0,
        orgtypes: Optional[Union[List[str], Literal["all"]]] = None,
    ):
        orgtypes = self._get_orgtypes_from_str(orgtypes)
        SUGGEST_NAME = "name_complete"

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

    def suggest_type(
        self,
        request,
        prefix: str,
        cursor: int = 0,
    ):
        if not prefix:
            raise Http404("Prefix must be supplied")

        results = OrganisationType.objects.filter(
            Q(title__icontains=prefix) | Q(slug__icontains=prefix)
        )[cursor : cursor + 10]

        return {
            "result": [
                {
                    "id": r.slug,
                    "name": r.title,
                    "notable": [],
                }
                for r in results
            ]
        }

    def propose_properties(self, request, type_, limit=500):
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

    def data_extension(self, request, body: DataExtensionQuery) -> Dict:
        result = do_extend_query(
            ids=body.ids,
            properties=[p.__dict__ for p in body.properties],
        )
        rows = {}
        for row_id, row in result["rows"].items():
            rows[row_id] = {}
            for k, v in row.items():
                rows[row_id][k] = convert_value(v)

        return {
            "meta": result["meta"],
            "rows": rows,
        }
