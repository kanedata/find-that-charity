import datetime

from django.conf import settings
from django.http import JsonResponse
from django.urls import Resolver404, resolve
from ninja_extra.exceptions import Throttled
from sqlite_utils import Database
from ua_parser import user_agent_parser

from findthatcharity.api.throttling import APIAnonRateThrottle, APIRateThrottle


class XCLacksMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Clacks-Overhead"] = "GNU Terry Pratchett"
        return response


class FTCThrottleMiddleware:
    throttle_classes = [APIRateThrottle, APIAnonRateThrottle]

    def __init__(self, get_response):
        self.get_response = get_response

    def _check_throttle(self, request):
        throttle_durations = []

        # go through each throttle
        for throttle_class in self.throttle_classes:
            throttling = throttle_class()
            if not throttling.allow_request(request):
                # Filter out `None` values which may happen in case of config / rate
                duration = throttling.wait()
                if duration is not None:
                    throttle_durations.append(duration)

        if throttle_durations:
            duration = max(throttle_durations, default=None)
            raise Throttled(duration)

    def __call__(self, request):
        response = self.get_response(request)
        if not response.headers.get("Content-Type", "").startswith("application/json"):
            return response

        try:
            self._check_throttle(request)
        except Throttled as exc:
            return JsonResponse(
                {
                    "success": False,
                    "error": exc.detail,
                },
                status=exc.status_code,
                headers={"Retry-After": "{:.0f}".format(float(exc.wait or 0.0))},
            )

        return response


class FTCLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        if settings.LOGGING_DB:
            self.db_args = dict(
                filename_or_conn=settings.LOGGING_DB.format(
                    year=datetime.datetime.now().year,
                    month=datetime.datetime.now().month,
                    day=datetime.datetime.now().day,
                )
            )
        else:
            self.db_args = dict(memory=True)

    def _get_db(self):
        return Database(**self.db_args)

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(request.META.get("HTTP_USER_AGENT"), str):
            ua = user_agent_parser.Parse(request.META.get("HTTP_USER_AGENT"))
        else:
            ua = None
        try:
            resolver_match = resolve(request.path_info)
        except Resolver404:
            resolver_match = None
        self._get_db()["logs"].insert(
            {
                "app": "findthatcharity",
                "timestamp": datetime.datetime.now().isoformat(),
                "url": request.build_absolute_uri(),
                "path": request.path,
                "method": request.method,
                "params": dict(request.GET.lists()),
                "origin": None,
                "referrer": request.META.get("HTTP_REFERER"),
                # "remote_addr": request.remote_addr,  # we don't collect IP address
                "endpoint": resolver_match.view_name if resolver_match else None,
                "view_args": resolver_match.kwargs if resolver_match else None,
                "user_agent_string": ua.get("string") if ua else None,
                "user_agent": {k: v for k, v in ua.items() if k != "string"}
                if ua
                else None,
                "status_code": response.status_code,
                "response_size": response.get("Content-Length", ""),
                "content_type": response.get("Content-Type", "").replace(
                    "; charset=utf-8", ""
                ),
            },
        )
        return response
