import json
import logging
import os
from typing import Tuple
from unittest.mock import patch

import jsonschema

from ftc.documents import CompanyDocument

from .conftest import ReconTestCase

logger = logging.getLogger(__name__)

with open(
    os.path.join(os.path.dirname(__file__), "data", "company_reconcile_response.json")
) as f:
    RECON_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "reconcile_response_empty.json")
) as f:
    EMPTY_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "company_mapping_response.json")
) as f:
    SUGGEST_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "company_extend_response.json")
) as f:
    EXTEND_RESPONSE = json.load(f)

RECON_BASE_URLS: list[Tuple[str, list[str]]] = [
    ("/api/v1/reconcile/company", ["0.2"]),
]


class TestCompanyReconcileAPI(ReconTestCase):
    def setUp(self):
        super().setUp()

        # setup elasticsearch patcher
        self.es_index_patcher = patch.object(CompanyDocument, "_index")
        self.addCleanup(self.es_index_patcher.stop)
        self.mock_es_index = self.es_index_patcher.start()

        # setup elasticsearch patcher
        self.es_mget_patcher = patch.object(CompanyDocument, "mget")
        self.addCleanup(self.es_mget_patcher.stop)
        self.mock_es_mget = self.es_mget_patcher.start()

    def test_get_company_service_spec(self):
        for base_url, schema_version, schema, method in self.get_test_cases(
            "manifest.json", RECON_BASE_URLS
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(method, "/api/v1/reconcile/company")
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
                            {"id": "registered-company", "name": "Registered Company"}
                        ],
                        "view": {"url": "http://testserver/company/{{id}}"},
                        "suggest": {
                            "property": {
                                "service_url": "http://testserver/api/v1/reconcile/company",
                                "service_path": "/suggest/property",
                            },
                            "type": {
                                "service_url": "http://testserver/api/v1/reconcile/company",
                                "service_path": "/suggest/type",
                            },
                        },
                        "extend": {
                            "propose_properties": {
                                "service_url": "http://testserver/api/v1/reconcile/company",
                                "service_path": "/extend/propose",
                            },
                            "property_settings": [],
                        },
                    },
                )

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_company_reconcile(self):
        self.mock_es.return_value.search.return_value = RECON_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "reconciliation-result-batch.json", RECON_BASE_URLS, ["GET", "POST"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(
                    method,
                    base_url,
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

    def test_company_reconcile_two(self):
        self.mock_es.return_value.search.return_value = RECON_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "reconciliation-result-batch.json", RECON_BASE_URLS, ["GET", "POST"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(
                    method,
                    base_url,
                    {
                        "queries": json.dumps(
                            {
                                "q0": {
                                    "query": "Kane data",
                                    "type": "/registered-company",
                                    "type_strict": "should",
                                },
                                "q1": {
                                    "query": "Tesco",
                                    "type": "/registered-company",
                                    "type_strict": "should",
                                },
                            }
                        ),
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["q0", "q1"])
                self.assertEqual(len(data["q0"]["result"]), 10)
                self.assertEqual(data["q0"]["result"][0]["id"], "12345670")

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_empty(self):
        self.mock_es.return_value.search.return_value = EMPTY_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "reconciliation-result-batch.json", RECON_BASE_URLS, ["GET", "POST"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(
                    method,
                    base_url,
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

    def test_reconcile_empty_query(self):
        self.mock_es.return_value.search.return_value = RECON_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "reconciliation-result-batch.json", RECON_BASE_URLS, ["GET", "POST"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(
                    method,
                    base_url,
                    {
                        "queries": json.dumps({"q0": {"query": ""}}),
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

    def test_reconcile_propose_properties(self):
        self.mock_es_index.get_mapping.return_value = SUGGEST_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "data-extension-property-proposal.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                properties_url = "".join(
                    list(service_spec["extend"]["propose_properties"].values())
                )

                response = self.do_request(
                    method,
                    properties_url,
                    dict(type="Company"),
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(
                    sorted(data.keys()), sorted(["properties", "type", "limit"])
                )
                self.assertEqual(data["type"], "Company")
                self.assertEqual(len(data["properties"]), 6)
                ids = [p["id"] for p in data["properties"]]
                self.assertTrue("CompanyStatus" in ids)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_property(self):
        self.mock_es_index.get_mapping.return_value = SUGGEST_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-properties-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                if "property" not in service_spec["suggest"]:
                    continue
                suggest_url = "".join(
                    list(service_spec["suggest"]["property"].values())
                )

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "company",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 4)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(data["result"][0]["id"], "CompanyCategory")
                self.assertEqual(len(data["result"][0]["notable"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_property_empty(self):
        self.mock_es_index.get_mapping.return_value = SUGGEST_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-properties-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                if "property" not in service_spec["suggest"]:
                    continue
                suggest_url = "".join(
                    list(service_spec["suggest"]["property"].values())
                )

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "BLAH",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_type(self):
        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-types-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                if "type" not in service_spec["suggest"]:
                    continue
                suggest_url = "".join(list(service_spec["suggest"]["type"].values()))

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "guarantee",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 2)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(
                    data["result"][0]["id"],
                    "private-limited-guarant-nsc-limited-exemption",
                )
                self.assertEqual(len(data["result"][0]["notable"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_type_empty(self):
        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-types-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                if "type" not in service_spec["suggest"]:
                    continue
                suggest_url = "".join(list(service_spec["suggest"]["type"].values()))

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "BLAH",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_extend(self):
        expected_tests = 2
        self.mock_es_mget.return_value = [
            (CompanyDocument.from_es(obj) if obj["found"] else None)
            for obj in EXTEND_RESPONSE["docs"]
        ]

        for base_url, schema_version, schema, method in self.get_test_cases(
            "data-extension-response.json", RECON_BASE_URLS, ["GET", "POST"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(
                    method,
                    base_url,
                    {
                        "extend": json.dumps(
                            {
                                "ids": [
                                    "GB-COH-00445790",
                                    "GB-COH-14015213",
                                    "GB-COH-BLAHBLAH",
                                ],
                                "properties": [
                                    {
                                        "id": "CompanyName",
                                    }
                                ],
                            }
                        )
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["meta", "rows"])
                self.assertEqual(
                    data["meta"], [{"id": "CompanyName", "name": "CompanyName"}]
                )
                self.assertEqual(
                    list(data["rows"].keys()),
                    ["GB-COH-00445790", "GB-COH-14015213", "GB-COH-BLAHBLAH"],
                )
                self.assertEqual(
                    data["rows"]["GB-COH-00445790"]["CompanyName"],
                    [{"str": "TESCO PLC"}],
                )
                self.assertEqual(data["rows"]["GB-COH-BLAHBLAH"]["CompanyName"], [{}])

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)
