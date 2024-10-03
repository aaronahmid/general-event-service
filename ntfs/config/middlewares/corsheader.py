#!/usr/bin/env python3
from django.conf import settings

ALLOWED_ORIGINS = settings.CORS_ALLOWED_ORIGINS
ALLOWED_METHODS = settings.CORS_ALLOW_METHODS
ALLOWED_HEADERS = settings.CORS_ALLOW_HEADERS


class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Replace '*' with your front-end URL in production for the 'Origin' header.
        response["Access-Control-Allow-Origin"] = ", ".join(ALLOWED_ORIGINS)
        response["Access-Control-Allow-Methods"] = ", ".join(ALLOWED_METHODS)
        response["Access-Control-Allow-Headers"] = ", ".join(ALLOWED_HEADERS)

        return response
