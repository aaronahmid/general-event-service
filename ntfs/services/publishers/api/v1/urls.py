#!/usr/bin/env python3
"""payment service api url mappings"""
from django.urls import path
from .endpoints import EventPublisher

app_name = "publisher:v1"

urlpatterns = [
    path("publish/", EventPublisher.as_view(), name="event-publisher"),
]
