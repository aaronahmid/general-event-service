#!/usr/bin/env python3
"""API Client Module"""
import re
from typing import Dict, Any
import requests
import json
from services.exceptions import APIClientException


class APIClient:
    """API Client Class
    :param base_url: Base URL for the API
    :param auth: Authentication type (API Key, OAuth, etc.)
    :type base_url: str
    :type auth: str

    :Example:

    >>> from api_client import APIClient
    >>> client = APIClient('https://api.example.com', '1234567890')
    >>> client.request('get', '/users')
    >>> print(client.json)

    :Methods:
    - request(method: str = 'get', resource_path: str = '/', data: Any = None, headers: Dict[str, str] = None) -> None
    - json
    - status_code
    - ok
    - text
    - content
    - cookies
    - elapsed
    - encoding
    - history
    - is_redirect
    - is_permanent_redirect
    - links
    - next
    - url

    :Attributes:
    - METHODS
    - CONTENT_TYPE
    - response
    - base_url
    - auth
    - headers
    """

    METHODS = {
        "post": requests.post,
        "get": requests.get,
        "put": requests.put,
        "delete": requests.delete,
    }
    # CONTENT_TYPE = "application/json"
    response: requests.Response | Any = {}

    def __init__(self, base_url: str, auth: str) -> None:
        """Constructor Method
        :param base_url: Base URL for the API
        :param auth: Authentication type
        :type base_url: str
        :type auth: str

        :Example:

        >>> from api_client import APIClient
        >>> client = APIClient('https://api.example.com', '1234567890')
        """
        self.base_url = base_url
        self.auth = auth
        self.headers = {}

    def request(
        self,
        method: str = "get",
        resource_path: str = "/",
        data: Any = None,
        headers: Dict[str, str] | Any = None,
        verify: bool = True,
    ) -> None:
        url = self.base_url + resource_path
        if headers:
            self.headers.update(headers)

        if data and isinstance(data, dict):
            request_data = json.dumps(data)
        elif data and isinstance(data, dict) is False:
            request_data = data
        else:
            request_data = None

        # print(request_data)

        # print(request_data)
        # print(headers)
        make_request = self.METHODS.get(method.lower(), "get")
        response = make_request(
            url, data=request_data, headers=self.headers, verify=verify
        )
        self.response = response

    # Property Decorators
    @property
    def json(self):
        try:
            json_data = self.response.json()
        except Exception:
            raise APIClientException(
                detail={
                    "message": "client didn't return a json see the content",
                    "content": self.response.content,
                },
                status_code=self.response.status_code,
            )

        return json_data

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def ok(self):
        return self.response.ok

    @property
    def text(self):
        return self.response.text

    @property
    def content(self):
        return self.response.content

    @property
    def cookies(self):
        return self.response.cookies

    @property
    def elapsed(self):
        return self.response.elapsed

    @property
    def encoding(self):
        return self.response.encoding

    @property
    def history(self):
        return self.response.history

    @property
    def is_redirect(self):
        return self.response.is_redirect

    @property
    def is_permanent_redirect(self):
        return self.response.is_permanent_redirect

    @property
    def links(self):
        return self.response.links

    @property
    def next(self):
        return self.response.next

    @property
    def url(self):
        return self.response.url
