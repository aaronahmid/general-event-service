#!/usr/bin/env python3
from typing import Any
from django.conf import settings
from django.http import HttpResponseForbidden

allowed_ips = settings.ALLOWED_IPS


class BlockIPNotInWhiteList:
    def __init__(self, get_response, allowed_ips) -> None:
        self.get_response = get_response
        self.allowed_ips = allowed_ips

    def __call__(self, request):
        # -- get client ip --
        client_ip = request.META.get('REMOTE_ADDR')

        if client_ip not in self.allowed_ips:
            HttpResponseForbidden("Access Forbidden")

        response = self.get_response(request)
        return response
