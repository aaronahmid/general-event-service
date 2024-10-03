#!/usr/bin/env python3
"""login api view with knox"""
# REST FRAMEWORK
from coreapi import Client
from rest_framework import permissions, generics, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from yaml import serialize
from services.clients.oauthclient import get_employee, OAuthClient, get_app
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

# KNOX
from knox.models import AuthToken

# serializers
from services.authservice.api.common.serializers import (
    UserSerializer,
    LoginUserSerializer,
    DuplicateTokenSerializer,
)

from services.exceptions import (
    exception_handler,
    handle_error_response,
    APIClientException,
)

import datetime

from django.conf import settings

from config.settings import getvar

import binascii
import os

from django.utils import timezone

from knox.settings import knox_settings
from rest_framework.views import APIView

from core.models import User, RefreshToken

from services.utils import Cache

from services.exceptions import ObjectNotFoundError

import json

from typing import Any

services_variable: Any = getvar("services")
services: dict = json.loads(services_variable)

# print(f"services: {services}")


def generate_60min_timestamp(min: int = 60):
    # Get the current time
    current_time = datetime.datetime.now()

    # Add 30 minutes to the current time
    time_in_minutes_from_now = current_time + datetime.timedelta(minutes=min)

    # Convert the result to a timestamp (Unix timestamp, which is the number of seconds since January 1, 1970)
    timestamp = int(time_in_minutes_from_now.timestamp())

    return timestamp


class LoginAPIView(generics.GenericAPIView):
    """
    logs a user in using a basic authentication method

    Args:
        email: user's email address
        password: user's password

    Returns: [user_object, auth_token]
    """

    authentication_classes = [BasicAuthentication]
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginUserSerializer
    sid = getvar("SERVICE_ID")

    def post(self, request, *args: tuple, **kwargs: dict) -> Response:
        """
        handles the post data sent to 'auth/api/v1/login'

        Args:
            request (object): clients request

        Returns:
            user: the user's object
            Token: user token
        """
        try:
            # -- validate email and password --
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data

            # -- get the employee trying to login --
            request.user = user
            # get_employee(request)

            # -- create auth token
            # and refresh token --
            instance, auth_token = AuthToken.objects.create(user=user)  # type: ignore

            refresh_token = self.create_refresh_token(instance)

            # -- duplicate token on services
            # that user has access on --
            # print(request.iam_user, "IAM USER")
            # self.duplicate_token_on_services(
            #     instance, refresh_token, auth_token, request.iam_user
            # )

        except Exception as error:
            response = exception_handler(
                exc=error, context="something went wrong while login you in"
            )
            return handle_error_response(response, error)

        # account_info = request.iam_user
        # account_info.pop("user")

        response = {
            "message": "Login Successful",
            "status_code": 200,
            "payload": {
                "user": UserSerializer(user).data,
                "token": auth_token,
                "refresh_token": refresh_token.refresh_token,
                "expire_at": generate_60min_timestamp(settings.TOKEN_EXPIRE_AT),
                # "account_info": account_info,
            },
        }

        return Response(response, status=status.HTTP_200_OK)

    def create_refresh_token(self, auth_token):
        # Generate a new refresh token
        refresh_token = binascii.hexlify(os.urandom(24)).decode()
        return RefreshToken.objects.create(
            auth_token=auth_token, refresh_token=refresh_token, user=auth_token.user
        )

    def duplicate_token_on_services(
        self, instance, refresh_token, auth_token, iam_user
    ):
        print("duplicating token...")
        cache = Cache(timeout=86400)
        service_ids = iam_user.get("employee", {}).get("active_on", [])

        # print(service_ids)

        iam_system = get_app()

        for service_id in service_ids:
            sid = service_id.get("id")

            # print(sid)

            # -- avoid making calls to this service --
            # -- fetch some info about the service --
            if sid != self.sid:
                service_data = cache.get(f"service_{sid}")
                if service_data is None:
                    print("get service")
                    client = OAuthClient(system=iam_system)
                    client.make_request("get", f"/systems/{sid}")

                    if client.status_code == 200:
                        service_data = client.json
                        print("successfully fetched service info")

                    else:
                        print(f"failed to get service '{sid}' info, operation aborted")
                        raise APIClientException(
                            f"operation failed please try again: {client.text}",
                            code=client.status_code,
                        )

                    cache.set(f"service_{sid}", service_data)

                # -- build client credentials
                # and initialize client --
                # print(service_data)

                service: Any = services.get(sid)

                client_data = {
                    "sid": service_data.get("sid", "uuid"),
                    "url_endpoint": service_data.get("url_endpoint", "url"),
                    "system_client_id": service.get("system_client_id"),
                    "system_client_secret": service.get("system_client_secret"),
                    "token_endpoint": service_data.get("token_endpoint", "endpoint"),
                    "redirect_uri": service_data.get("redirect_uri"),
                }
                # print(client_data)

                try:
                    client = OAuthClient(system=client_data)

                    # print(f"access toke: {client.access_token}")

                    # -- build token instance data --
                    # -- make call --

                    # print(refresh_token)
                    token_data = {
                        "digest": instance.digest,
                        "token_key": instance.token_key,
                        "refresh_token": refresh_token.refresh_token,
                        "user": f"{instance.user.user_id}",
                        "expiry": f"{instance.expiry}",
                        "auth_token": auth_token,
                    }

                    # print(token_data)
                    client.make_request(
                        "post", "/api/v1/auth/duplicate-token/", data=token_data
                    )

                    if client.status_code == 200:
                        print("successfully duplicated token")

                    else:
                        print({client.text})
                        print(
                            f"failed to duplicate token on '{sid}', operation aborted"
                        )
                        raise APIClientException(
                            f"{client.text}", code=client.status_code
                        )
                except Exception as error:
                    raise error


class DuplicateTokenView(APIView):
    permission_classes = [TokenHasReadWriteScope]

    def post(self, request, *args, **kwargs):
        try:
            serializer = DuplicateTokenSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            data = request.data

            user_id = data.get("user")

            try:
                user = User.objects.get(user_id=user_id)
            except User.DoesNotExist:
                raise ObjectNotFoundError("User does not exists on this service")

            instance, auth_token = AuthToken.objects.create(user=user)  # type: ignore
            instance.token_key = data.get("token_key")
            instance.digest = data.get("digest")
            instance.expiry = data.get("expiry")
            instance.save()

            self.create_refresh_token(instance, data.get("refresh_token"), user)

        except Exception as error:
            response = exception_handler(error, "error while duplicating token")
            return handle_error_response(response, error)

        return Response(
            {"message": "token duplicated successfully!"}, status=status.HTTP_200_OK
        )

    def create_refresh_token(self, auth_token, refresh_token, user):
        # duplicate refresh token
        return RefreshToken.objects.create(
            auth_token=auth_token, refresh_token=refresh_token, user=user
        )


class RefreshTokenView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Assuming the RefreshToken model has a `refresh_token` field
            refresh_token_instance = RefreshToken.objects.get(
                refresh_token=refresh_token
            )
            user = refresh_token_instance.user

            # Check if the token is expired
            if refresh_token_instance.is_expired:
                refresh_token_instance.delete()
                return Response(
                    {"error": "Refresh token has expired"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                request.user = user
                get_employee(request)
            except Exception as error:
                response = exception_handler(
                    exc=error, context="something went wrong while login you in"
                )
                return handle_error_response(response, error)

            instance, token = AuthToken.objects.create(user)  # type: ignore

            # Optionally, create a new refresh token and delete the old one
            refresh_token_instance.delete()
            new_refresh_token = self.create_refresh_token(instance)

            return Response(
                {
                    "token": token,
                    "refresh_token": new_refresh_token.refresh_token,
                    "expire_at": generate_60min_timestamp(settings.TOKEN_EXPIRE_AT),
                }
            )

        except RefreshToken.DoesNotExist:
            return Response(
                {"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST
            )

    def create_refresh_token(self, auth_token):
        # Generate a new refresh token
        refresh_token = binascii.hexlify(os.urandom(24)).decode()
        return RefreshToken.objects.create(
            auth_token=auth_token, refresh_token=refresh_token, user=auth_token.user
        )
