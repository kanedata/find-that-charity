import json
import logging
import os

import jsonschema
from referencing import Registry

from ftc.tests import TestCase

from .conftest import get_schema, retrieve_schema_from_filesystem

logger = logging.getLogger(__name__)

with open(
    os.path.join(os.path.dirname(__file__), "data", "company_reconcile_response.json")
) as f:
    RECON_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "reconcile_response_empty.json")
) as f:
    EMPTY_RESPONSE = json.load(f)


class TestCompanyReconcileAPI(TestCase):
    def setUp(self):
        super().setUp()
        self.registry = Registry(retrieve=retrieve_schema_from_filesystem)

    # GET request to /api/v1/reconcile/company should return the service spec
    def test_get_company_service_spec(self):
        for schema_version, schema in get_schema("manifest.json").items():
            with self.subTest(schema_version):
                response = self.client.get("/api/v1/reconcile/company")
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(
                    data,
                    {
                        "versions": ["0.2"],
                        "name": "Find that Charity Company Reconciliation API",
                        "identifierSpace": "http://org-id.guide",
                        "schemaSpace": "https://schema.org",
                        "defaultTypes": [
                            {"id": "/registered-company", "name": "Registered Company"}
                        ],
                        "view": {"url": "http://testserver/company/{{id}}"},
                    },
                )

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    # POST request to /api/v1/reconcile/company should return a list of candidates
    def test_company_reconcile(self):
        # attach RECON RESPONSE to the search() method of self.mock_es
        self.mock_es.return_value.search.return_value = RECON_RESPONSE

        for schema_version, schema in get_schema(
            "reconciliation-result-batch.json"
        ).items():
            with self.subTest(schema_version):
                response = self.client.post(
                    "/api/v1/reconcile/company",
                    {
                        "queries": json.dumps({"q0": {"query": "Test"}}),
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["q0"])
                self.assertEqual(len(data["q0"]["result"]), 10)
                self.assertEqual(data["q0"]["result"][0]["id"], "12345670")

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    # POST request to /api/v1/reconcile should return a list of candidates
    def test_reconcile_empty(self):
        # attach RECON RESPONSE to the search() method of self.mock_es
        self.mock_es.return_value.search.return_value = EMPTY_RESPONSE

        for schema_version, schema in get_schema(
            "reconciliation-result-batch.json"
        ).items():
            with self.subTest(schema_version):
                response = self.client.post(
                    "/api/v1/reconcile/company",
                    {
                        "queries": json.dumps({"q0": {"query": "Test"}}),
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["q0"])
                self.assertEqual(len(data["q0"]["result"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
