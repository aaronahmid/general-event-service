#!/usr/bin/env python3
"""auth service url mapping"""
from django.urls import path, include

app_name = "auth service"

urlpatterns = [
    path("v1/auth/", include("services.authservice.api.v1.urls", "v1")),
    path("v1.2/auth/", include("services.authservice.api.v1.urls", "v1.2")),
]
