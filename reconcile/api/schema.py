from typing import List, Union, Dict, Literal

from ninja import Schema


class Property(Schema):
    id: str
    name: str


class EntityType(Property):
    broader: List[dict] = None


class Entity(Property):
    description: str = None
    type: List[EntityType] = None


class PropertyValue(Schema):
    pid: str
    v: Union[
        str,
        bool,
        int,
        float,
        Entity,
        List[str],
        List[bool],
        List[int],
        List[float],
        List[Entity],
    ]


class MatchingFeature(Schema):
    id: str
    value: Union[bool, float, int]


class ReconciliationCandidate(Entity):
    score: float = None
    match: bool = False


class ReconciliationResult(Schema):
    __root__: List[ReconciliationCandidate]


class ReconciliationResultBatch(Schema):
    __root__: Dict[str, ReconciliationResult]


class ReconciliationQuery(Schema):
    query: str
    type: Union[str, List[str]] = None
    limit: int = None
    properties: List[PropertyValue] = None
    type_strict: Literal["should", "all", "any"] = None


class ReconciliationQueryBatch(Schema):
    __root__: Dict[str, ReconciliationQuery]
