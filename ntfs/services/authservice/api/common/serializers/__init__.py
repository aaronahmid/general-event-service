#!/usr/bin/env python3
"""initialize all serializers"""
from .user import (
    UserSerializer,
    UserCustomerSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer
)
from .login import LoginUserSerializer, DuplicateTokenSerializer