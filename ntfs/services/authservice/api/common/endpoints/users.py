#!/usr/bin/env python3
"""user.py
Auth user API endpoints
"""
# django core
from cgitb import reset
from django.shortcuts import get_object_or_404

# rest framework and oauth
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import serializers
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from rest_framework.decorators import action

# core models
from core.models import User

# serializers
from services.authservice.api.common.serializers import (
    UserSerializer,
    UserCustomerSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
)

# access view
from rest_access_policy.access_view_set_mixin import AccessViewSetMixin

# access policies
from services.authservice.api.common.policies import UserAccesPolicy

# utils
from services.exceptions.handle_error_response import handle_error_response
from services.utils.custom_pagination import CustomPagination
from services.utils.cache import Cache
from services.utils.functions import format_response_data
from services.exceptions.exception_handler import exception_handler
from django.db import transaction

from typing import Any

cache = Cache()


class UserViewset(AccessViewSetMixin, viewsets.ViewSet, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated | TokenHasReadWriteScope]
    pagination_class = CustomPagination
    queryset = User.objects.all()
    access_policy = UserAccesPolicy
    lookup_field = 'user_id'
    serializer_class = UserSerializer

    def get_queryset(self):
        return super().get_queryset()

    def get_object(self):
        return super().get_object()

    @transaction.atomic
    def create(self, request) -> Response:
        """create a new user

        Description
        -----------
        create a new user

        Access Permissions
        ------------------
        - `groups: [System Admin, group:Owners]`

        Json Parameters
        ---------------
        ```JSON
            {

            }
        ```


        Ex. Request
        -----------
        - ex. request
            ```JSON
                {

                }
            ```

        Ex. Response
        ------------
        - ex. response
            ```JSON
                {

                }
            ```
        """
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user = UserSerializer(user).data

        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = format_response_data(user, 201, "user created!")
        response = Response(data=data, status=status.HTTP_201_CREATED)
        return response

    def retrieve(self, request, *args, **kwargs):
        """Retrieve user

        Description
        -----------
        Retrieve a user by id


        Ex. Response
        ------------
        - ex. response
            ```JSON
                {

                }
            ```
        """
        try:
            user = self.get_object()
            user = UserSerializer(user).data
        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = format_response_data(user, 200)

        response = Response(data=data, status=status.HTTP_200_OK)

        return response

    def list(self, request) -> Response:
        """get users list

        Description
        -----------
        retrieves all users

        Access Permissions
        ------------------

        Ex. Response
        ------------
        - ex. response
            ```JSON
                {

                }
            ```
        """
        try:
            paginate = None

            page, page_size = request.query_params.get(
                "page", None
            ), request.query_params.get("page_size", None)

            if page is None and page_size is None:
                cached_results = cache.get("users")

            else:
                paginate = {"page": page, "page_size": page_size}
                cached_results = cache.get("users", paginate)

            if cached_results is not None:
                return Response(
                    data=cached_results, status=status.HTTP_200_OK, exception=False
                )

            queryset = self.get_queryset()

            queryset_page = self.paginate_queryset(queryset)

            serializer = UserSerializer(queryset, many=True)

            users = serializer.data

            # print(users)
            # print(page)

            if queryset_page is not None:
                paginated_response = self.get_paginated_response(serializer.data)
                cache.set("users", paginated_response.data, paginate)

                return paginated_response
        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = format_response_data(users, 200)
        response = Response(data, status=status.HTTP_200_OK)
        cache.set("users", response.data)
        return response

    @transaction.atomic
    def update(self, request, *args, **kwargs) -> Response:
        """update user

        Description
        -----------
        Update user

        Access Permission
        -----------------
        - `group: [System Admin, group:Owners]`

        Json Parameters
        ---------------
        ```JSON
            {

            }
        ```


        Ex. Request
        -----------
        - ex. request
            ```JSON
                {

                }
            ```

        Ex. Response
        ------------
        - ex. response
            ```JSON
                {

                }
            ```
        """
        try:
            user = self.get_object()
            serializer = UserSerializer(instance=user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user = UserSerializer(user).data

        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = format_response_data(user, 200, "user updated!")
        response = Response(data=data, status=status.HTTP_200_OK)
        cache.invalidate('users')
        cache.invalidate_many('users')
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.invalidate('users')
        cache.invalidate_many('users')
        return response

    @transaction.atomic
    @action(methods=["post", "put"], detail=True)
    def change_password(self, request, pk=None):
        """change logged in user password

        Description
        -----------
        only users can change their own password when they're logged in, if they forgot their password, then an admin must reset it for them.

        Access Permission
        -----------------
        - `groups: *`
        - `conditions: [is_user]

        Ex. Request
        -----------
        - ex. request
            ```JSON
                {
                "old_password": "code*beta*test",
                "new_password": "code1*beta*test"
                }
            ```

        Ex. Response
        ------------
        - ex. response
            ```JSON
                {
                "status": "success",
                "code": "200",
                "message": "Password updated successfully!"
                }
        """
        try:
            # employee = self.get_object()
            user = self.get_object()
            serializer: ChangePasswordSerializer | Any = ChangePasswordSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            if not user.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()

        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = {
            "status": "success",
            "code": "200",
            "message": "Password updated successfully!",
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(methods=["post", "put"], detail=True)
    def reset_password(self, request, *args, **kwargs):
        """Reset user password

        Description
        -----------
        resets a user's password

        Access Permission
        -----------------
        - `groups: [System Admin, Owners]`

        Json Parameters
        ---------------
        ```JSON
            {
            "new_password": "string | new password old password",
            "verify_password": "string | enter new password again, verify that both passwords match"
            }
        ```


        Ex. Request
        -----------
        - ex. request
            ```JSON
                {
                "new_password": "code*beta*test",
                "verify_password": "code1*beta*test"
                }
            ```

        Ex. Response
        ------------
        - ex. response
            ```JSON
                {
                "status": "success",
                "code": "200",
                "message": "Password updated successfully!"
                }
            ```
        """
        try:
            # employee = self.get_object()
            user = self.get_object()
            serializer: ResetPasswordSerializer | Any = ResetPasswordSerializer(
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            # set_password also hashes the password that the user will get
            verified = serializer.verify_password(request.data)
            if verified:
                user.set_password(serializer.data.get("new_password"))
                user.save()
            else:
                raise serializers.ValidationError("new password doesn't match")
        except Exception as error:
            response = exception_handler(error, "An error occured")
            return handle_error_response(response, error)

        data = format_response_data(
            {},
            200,
            "Password updated successfully!",
        )
        return Response(data=data, status=status.HTTP_200_OK)
