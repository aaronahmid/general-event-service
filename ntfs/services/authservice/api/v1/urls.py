#!/usr/bin/env python3
"""auth service url mapping"""
from django.urls import path

# rest framework default api router
from rest_framework.routers import DefaultRouter

# views and viewsets
from services.authservice.api.v1.endpoints import (
    UsersAPI,
    LoginAPI,
    # RefreshTokenAPI,
    DuplicateTokenAPI,
)

# knox views
from knox import views as knox_views

app_name = "auth_service_v1"

router = DefaultRouter()
router.register("users", UsersAPI, basename="users")

urlpatterns = [
    path("login/", LoginAPI.as_view(), name="login"),
    # path("refresh-token/", RefreshTokenAPI.as_view(), name="refresh_token"),
    path("duplicate-token/", DuplicateTokenAPI.as_view(), name="duplicate_token"),
    path("logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
]
urlpatterns += router.urls
