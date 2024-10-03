#!/usr/bin/env python3
"""login serializer"""
from rest_framework import serializers
from django.contrib.auth import authenticate


class DuplicateTokenSerializer(serializers.Serializer):
    digest = serializers.CharField()
    token_key = serializers.CharField()
    refresh_token = serializers.CharField()
    user = serializers.CharField()
    expiry = serializers.CharField()
    auth_token = serializers.CharField()


class LoginUserSerializer(serializers.Serializer):
    """User login serializer"""
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, credentials: dict):
        """
        validates login data

        Args:
            credentials [dict]: user login credentials

        Returns:
            user [dic]: user serialized data
        """
        # credentials['email'] = credentials.get('email', '').lower()
        user = authenticate(**credentials)
        if user:
            # check if user is active
            # if user.is_active:
            return user
            # return {'warnings': 'inactive user', 'user': user}
        raise serializers.ValidationError('Invalid Credentials or User is inactive')
