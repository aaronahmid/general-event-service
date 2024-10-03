#!/usr/bin/env python3
"""payment service api url mappings"""
from django.urls import path, include

app_name = "publishers"

urlpatterns = [
    path("v1/", include("services.publishers.api.v1.urls", "v1")),
]
