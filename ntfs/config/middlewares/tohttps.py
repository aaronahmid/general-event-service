#!/usr/bin/env python3
"""redirect http requests to https version
"""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class HTTPSRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.is_secure() and not settings.DEBUG:
            secure_url = request.build_absolute_uri()
            secure_url = secure_url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(secure_url)
        return self.get_response(request)
