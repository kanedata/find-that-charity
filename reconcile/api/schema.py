from enum import Enum
from typing import Dict, List, Literal, Optional, TypeVar, Union

from ninja import Schema
from pydantic import RootModel

# Reconciliation API Schema
#
# Based on version 0.2 of the schema
# https://www.w3.org/community/reports/reconciliation/CG-FINAL-specs-0.2-20230410/#service-manifest
#


class EntityType(Schema):
    id: str
    name: str
    broader: Optional[List["EntityType"]] = None


class Entity(Schema):
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[List[EntityType]] = None


class Property(Schema):
    id: str
    name: str


PropertyValue = TypeVar("PropertyValue", str, int, bool, float, Entity)


class QueryProperty(Schema):
    pid: str
    v: PropertyValue


class UrlSchema(Schema):
    url: str


class PreviewMetadata(Schema):
    url: str = None
    width: int = 430
    height: int = 300


class PropertySettingChoice(Schema):
    name: str
    value: str


class DataExtensionPropertySetting(Schema):
    name: str
    label: str
    type: Optional[Literal["number", "text", "checkbox", "select"]] = None
    default: Optional[str] = None
    help_text: Optional[str] = None
    choices: Optional[List[PropertySettingChoice]] = None


class DataExtensionProperty(Schema):
    id: str
    name: str = None
    settings: DataExtensionPropertySetting = None


class DataExtensionPropertyProprosal(Schema):
    service_url: str
    service_path: str


class DataExtensionMetadata(Schema):
    propose_properties: Optional[DataExtensionPropertyProprosal] = None
    property_settings: List[DataExtensionPropertySetting] = []


class DataExtensionPropertyProposalResponse(Schema):
    properties: List[Property]
    type: str
    limit: int = 10


class DataExtensionQuery(Schema):
    ids: List[str]
    properties: List[DataExtensionProperty]


class DataExtensionPropertyResponse(Schema):
    id: str
    values: List[Dict]


class DataExtensionQueryResponse(Schema):
    meta: List[Entity]
    rows: Dict[str, Dict]


class SuggestMetadata(Schema):
    service_url: str
    service_path: str
    flyout_service_url: str = None
    flyout_service_path: str = None


class ServiceSpecSuggest(Schema):
    entity: Optional[SuggestMetadata] = None
    property: Optional[SuggestMetadata] = None
    type: Optional[SuggestMetadata] = None


class ReconciliationServiceVersions(str, Enum):
    v0_1 = "0.1"
    v0_2 = "0.2"


class OpenAPISecuritySchemeType(str, Enum):
    apikey = "apiKey"
    http = "http"
    mutualTLS = "mutualTLS"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"


class OpenAPISecuritySchema(Schema):
    type: OpenAPISecuritySchemeType
    description: Optional[str] = None
    name: Optional[str] = None
    in_: Optional[str] = None
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional[Dict] = None
    openIdConnectUrl: Optional[str] = None


class ServiceSpec(Schema):
    versions: Optional[List[ReconciliationServiceVersions]] = [
        ReconciliationServiceVersions.v0_2
    ]
    name: str = "Reconciliation API"
    identifierSpace: str = "http://org-id.guide"
    schemaSpace: str = "https://schema.org"
    defaultTypes: List[EntityType] = []
    documentation: Optional[str] = None
    logo: Optional[str] = None
    serviceVersion: Optional[str] = None
    view: UrlSchema
    feature_view: Optional[UrlSchema] = None
    preview: Optional[PreviewMetadata] = None
    suggest: Optional[ServiceSpecSuggest] = None
    extend: Optional[DataExtensionMetadata] = None
    batchSize: Optional[int] = None
    authentication: Optional[OpenAPISecuritySchema] = None


class ReconciliationQuery(Schema):
    query: str
    type: Optional[EntityType] = None
    limit: int = 10
    properties: Optional[List[QueryProperty]] = None
    type_strict: Optional[Literal["should", "all", "any"]] = None


class ReconciliationQueryBatch(Schema):
    queries: Dict[str, ReconciliationQuery]


class ReconciliationQueryBatchForm(Schema):
    queries: str = None
    extend: str = None


class MatchingFeature(Schema):
    id: str
    name: str
    value: Union[bool, int, float]


class ReconciliationCandidate(Schema):
    id: str
    name: str
    description: Optional[str] = None
    type: List[EntityType] = []
    score: float
    features: Optional[List[MatchingFeature]] = None
    match: bool = False


class ReconciliationResult(Schema):
    result: List[ReconciliationCandidate]


class ReconciliationResultBatch(RootModel[Dict[str, Dict]], Schema):
    root: Dict[str, ReconciliationResult]


class SuggestResult(Schema):
    id: str
    name: str
    description: str = None
    notable: Optional[Union[List[EntityType], List[str]]] = None


class SuggestResponse(Schema):
    result: List[SuggestResult]
