#!/usr/bin/env python3
"""auth service v1 endpoints initialization"""
from services.authservice.api.common.endpoints.users import UserViewset
from services.authservice.api.common.endpoints.login import LoginAPIView, DuplicateTokenView, RefreshTokenView
from services.authservice.api.common.endpoints.token import TokenAPIBaseClass