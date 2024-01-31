import json
import os
import re
import warnings

from referencing.jsonschema import DRAFT7

SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "specs")
SUPPORTED_API_VERSIONS = ["0.2"]


def get_schema(
    filename: str, supported_api_versions: list[str] = SUPPORTED_API_VERSIONS
) -> dict[str, dict]:
    schemas = {}
    for f in os.scandir(SCHEMA_DIR):
        if not f.is_dir():
            continue
        if f.name not in supported_api_versions:
            continue
        schema_path = os.path.join(f.path, filename)
        if os.path.exists(schema_path):
            with open(schema_path, encoding="utf8") as schema_file:
                schemas[f.name] = json.load(schema_file)
        else:
            msg = f"Schema file {schema_path} not found"
            warnings.warn(msg)
    return schemas


# set up jsonschema registry
def retrieve_schema_from_filesystem(uri: str):
    recon_schema = re.match(
        r"https://reconciliation-api\.github\.io/specs/(.*)/schemas/(.*\.json)",
        uri,
    )
    if recon_schema:
        schema_version = recon_schema.group(1)
        schema_file = recon_schema.group(2)
        return DRAFT7.create_resource(
            get_schema(schema_file, supported_api_versions=[schema_version])[
                schema_version
            ]
        )

    raise ValueError(f"Unknown URI {uri}")
