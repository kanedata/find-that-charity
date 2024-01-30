from typing import Dict, List, Literal, Optional, TypeVar, Union

from ninja import Schema


class EntityType(Schema):
    id: str
    name: str
    broader: Optional[List["EntityType"]] = None


class Entity(Schema):
    id: str
    name: str
    description: Optional[str] = None
    type: List[EntityType] = []


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


class DataExtensionMetadata(Schema):
    propose_properties: bool = False
    property_settings: List[dict]


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
    rows: List[Dict]


class ServiceSpecSuggest(Schema):
    entity: bool = False
    property: bool = False
    type: bool = False


class ServiceSpec(Schema):
    versions: Optional[List[str]] = ["0.1", "0.2"]
    name: str = "Find that Charity Reconciliation API"
    identifierSpace: str = "http://org-id.guide"
    schemaSpace: str = "https://schema.org"
    documentation: Optional[str] = None
    logo: Optional[str] = None
    serviceVersion: Optional[str] = None
    defaultTypes: List[EntityType]
    view: UrlSchema
    feature_view: Optional[UrlSchema] = None
    preview: Optional[PreviewMetadata] = None
    suggest: Optional[ServiceSpecSuggest] = None
    extend: Optional[DataExtensionMetadata] = None
    batchSize: Optional[int] = None
    authentication: Optional[Dict] = None


class ReconciliationQuery(Schema):
    query: str
    type: Optional[EntityType] = None
    limit: int = 10
    properties: Optional[List[QueryProperty]] = None
    type_strict: Optional[Literal["should", "all", "any"]] = None


class ReconciliationQueryBatch(Schema):
    queries: Dict[str, ReconciliationQuery]


class ReconciliationQueryBatchForm(Schema):
    queries: str


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
    candidates: List[ReconciliationCandidate]


class ReconciliationResultBatch(Schema):
    results: List[ReconciliationResult]


class SuggestResult(Schema):
    id: str
    name: str
    description: str = None
    notable: Optional[Union[List[EntityType], List[str]]] = None


class SuggestResponse(Schema):
    result: List[SuggestResult]
