from typing import Optional

from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest
from ninja.compatibility.request import get_headers
from ninja_apikey.security import check_apikey
from ninja_extra.throttling import SimpleRateThrottle


class APIRateThrottle(SimpleRateThrottle):
    scope = "api"
    param_name = "X-API-Key"

    def _get_user(self, request: HttpRequest) -> Optional[AbstractBaseUser]:
        if request.user and request.user.is_authenticated:
            return request.user

        headers = get_headers(request)
        key = headers.get(self.param_name)
        return check_apikey(key)

    def _cache_key(self, ident: str) -> str:
        cache_key = self.cache_format % {"scope": self.scope, "ident": ident}
        return cache_key

    def get_cache_key(self, request: HttpRequest) -> Optional[str]:
        user = self._get_user(request)
        if user:
            ident = user.pk
        else:
            ident = self.get_ident(request)

        return self._cache_key(ident)


class APIAnonRateThrottle(APIRateThrottle):
    scope = "anon"

    def get_cache_key(self, request: HttpRequest) -> Optional[str]:
        user = self._get_user(request)
        if user:
            return None

        return self._cache_key(self.get_ident(request))
