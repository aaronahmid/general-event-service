#!/usr/bin/env python
""" access control user policies
"""
from typing import List
from rest_access_policy.access_policy import AccessPolicy


class UserAccesPolicy(AccessPolicy):
    """Defines access policy for users"""

    statements: List[dict]
    statements = [
        {
            "action": ["create", "destroy", "update"],
            "principal": ["group:System Admins", "group:Owners"],
            "effect": "allow",
        },
        {
            "action": ["list", "retrieve"],
            "principal": [
                "group:System Admins",
                "group:Owners",
            ],
            "effect": "allow",
        },
        {
            "action": ["reset_password"],
            "principal": ["group:System Admins"],
            "effect": "allow",
        },
        {
            "action": [
                "change_password",
            ],
            "principal": ["*"],
            "effect": "allow",
            "condition": ["is_user"],
        },
    ]

    def is_user(self, request, view, action: list) -> bool:
        """Is this the user"""
        try:
            user = view.get_object()
        except AssertionError:
            return False
        return user == request.user
