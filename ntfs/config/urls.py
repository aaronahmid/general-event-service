#!/usr/bin/env python3
"""global URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
import oauth2_provider.views as oauth2_views
from django.conf import settings
from services.authservice.api.v1.endpoints import TokenAPI

schema_view = get_schema_view(
    openapi.Info(
        title="NTFS",
        default_version="v1.2",
        description="A centralized event and notification handler for microservices",
        terms_of_service="",
        contact=openapi.Contact(email="aaronbahmid@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=False,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

# api url mappings
api = [
    path("", include("services.authservice.urls", namespace="auth_service")),
    path("", include("services.publishers.urls", namespace="publishers"))
]

# oauth url mapping
# OAuth2 provider endpoints
oauth2_endpoint_views = [
    path("authorize/", oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path("token/", TokenAPI.as_view(), name="token"),
    path("revoke-token/", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        path("applications/", oauth2_views.ApplicationList.as_view(), name="list"),
        path(
            "applications/register/",
            oauth2_views.ApplicationRegistration.as_view(),
            name="register",
        ),
        path(
            "applications/<pk>/",
            oauth2_views.ApplicationDetail.as_view(),
            name="detail",
        ),
        path(
            "applications/<pk>/delete/",
            oauth2_views.ApplicationDelete.as_view(),
            name="delete",
        ),
        path(
            "applications/<pk>/update/",
            oauth2_views.ApplicationUpdate.as_view(),
            name="update",
        ),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        path(
            "authorized-tokens/",
            oauth2_views.AuthorizedTokensListView.as_view(),
            name="authorized-token-list",
        ),
        path(
            "authorized-tokens/<pk>/delete/",
            oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete",
        ),
    ]

urlpatterns = [
    # oauth2 endpoints
    path(
        "api/v1/o/",
        include(
            (oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider"
        ),
    ),
    # version api endpoints
    path("api/", include(api), name="api"),
    # swagger docsb
    path("swagger.json/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    # -- only allow admin interface in debug mode --
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]
