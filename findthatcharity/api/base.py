from typing import List

from ninja import Schema
from ninja_extra import ControllerBase

from findthatcharity.api.throttling import APIAnonRateThrottle, APIRateThrottle


class APIControllerBase(ControllerBase):
    throttling_classes = [APIAnonRateThrottle, APIRateThrottle]


class ResultError(Schema):
    success: bool = False
    error: str = None
    params: dict = {}
    result: List = None


default_response = {401: ResultError, 403: ResultError, 404: ResultError}
