import json
import logging
import os
from typing import Tuple

import jsonschema

from .conftest import ReconTestCase

logger = logging.getLogger(__name__)

with open(
    os.path.join(os.path.dirname(__file__), "data", "all_reconcile_response.json")
) as f:
    RECON_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "reconcile_response_empty.json")
) as f:
    EMPTY_RESPONSE = json.load(f)

with open(
    os.path.join(os.path.dirname(__file__), "data", "all_suggest_response.json")
) as f:
    SUGGEST_RESPONSE = json.load(f)


RECON_BASE_URLS: list[Tuple[str, list[str]]] = [
    ("/api/v1/reconcile/", ["0.2"]),
    ("/reconcile", ["0.1"]),
    ("/reconcile/local-authority", ["0.1"]),
]


class TestReconcileAllAPI(ReconTestCase):
    def test_get_service_spec(self):
        for base_url, schema_version, schema, method in self.get_test_cases(
            "manifest.json", RECON_BASE_URLS
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                response = self.do_request(method, base_url)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                if not base_url.endswith("/"):
                    base_url += "/"
                if schema_version != "0.1":
                    self.assertEqual(data["versions"], ["0.2"])
                self.assertEqual(data["identifierSpace"], "http://org-id.guide")
                self.assertTrue("find that charity" in data["name"].lower())

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile(self):
        expected_tests = 6
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
                self.assertEqual(data["q0"]["result"][0]["id"], "GB-CHC-1006706")

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)

    def test_reconcile_empty_query(self):
        expected_tests = 6
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
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)

    def test_reconcile_with_type(self):
        expected_tests = 6
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
                                    "query": "Test",
                                    "type": "registered-charity",
                                    "type_strict": "should",
                                },
                                "q1": {
                                    "query": "Test",
                                    "type": "registered-charity",
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
                self.assertEqual(data["q0"]["result"][0]["id"], "GB-CHC-1006706")

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)

    def test_reconcile_empty(self):
        expected_tests = 6
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
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)

    def test_reconcile_suggest_entity(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-entities-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                suggest_url = "".join(list(service_spec["suggest"]["entity"].values()))

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "Test",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 5)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(data["result"][0]["id"], "GB-CHC-1110225")
                self.assertEqual(len(data["result"][0]["notable"]), 4)
                self.assertTrue("registered-charity" in data["result"][0]["notable"])

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_entity_type(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

        for base_url, schema_version, schema, method in self.get_test_cases(
            "suggest-entities-response.json", RECON_BASE_URLS, ["GET"]
        ):
            with self.subTest(
                base_url=base_url, schema_version=schema_version, method=method
            ):
                service_spec = self.client.get(base_url).json()
                suggest_url = "".join(list(service_spec["suggest"]["entity"].values()))

                response = self.do_request(
                    method,
                    suggest_url,
                    {
                        "prefix": "Test",
                        "type": "local-authority",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 5)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(data["result"][0]["id"], "GB-CHC-1110225")
                self.assertEqual(len(data["result"][0]["notable"]), 4)
                self.assertTrue("registered-charity" in data["result"][0]["notable"])

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_type(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

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
                        "prefix": "Charity",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 2)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(data["result"][0]["id"], "registered-charity")
                self.assertEqual(len(data["result"][0]["notable"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_type_empty(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

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

    def test_reconcile_suggest_property(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

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
                        "prefix": "name",
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["result"])
                self.assertEqual(len(data["result"]), 2)
                self.assertEqual(
                    list(data["result"][0].keys()), ["id", "name", "notable"]
                )
                self.assertEqual(data["result"][0]["id"], "name")
                self.assertEqual(len(data["result"][0]["notable"]), 0)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )

    def test_reconcile_suggest_property_empty(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

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

    def test_reconcile_extend(self):
        expected_tests = 6
        self.mock_es.return_value.search.return_value = RECON_RESPONSE

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
                                "ids": ["GB-CHC-1234", "GB-CHC-5"],
                                "properties": [
                                    {
                                        "id": "name",
                                    },
                                    {
                                        "id": "vocab-test-vocab",
                                    },
                                ],
                            }
                        )
                    },
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(list(data.keys()), ["meta", "rows"])
                self.assertEqual(data["meta"], [{"id": "name", "name": "Name"}])
                self.assertEqual(list(data["rows"].keys()), ["GB-CHC-1234", "GB-CHC-5"])
                self.assertEqual(
                    data["rows"]["GB-CHC-1234"]["name"],
                    [{"str": "Test organisation"}],
                )
                self.assertEqual(
                    data["rows"]["GB-CHC-1234"]["vocab-test-vocab"],
                    [{"str": "A"}, {"str": "B"}, {"str": "C"}],
                )

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
                expected_tests -= 1
        self.assertEqual(expected_tests, 0)

    def test_reconcile_propose_properties(self):
        self.mock_es.return_value.search.return_value = SUGGEST_RESPONSE

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
                    dict(type="Organization"),
                )
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(
                    sorted(data.keys()), sorted(["properties", "type", "limit"])
                )
                self.assertEqual(data["type"], "Organization")
                self.assertGreater(len(data["properties"]), 30)
                ids = [p["id"] for p in data["properties"]]
                self.assertTrue("dateRegistered" in ids)
                self.assertTrue("vocab-test-vocab" in ids)

                jsonschema.validate(
                    instance=data,
                    schema=schema,
                    cls=jsonschema.Draft7Validator,
                    registry=self.registry,
                )
