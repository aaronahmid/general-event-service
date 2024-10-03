"""handles responses v1
"""
from services.exceptions.errors import *
from rest_framework.response import Response
from rest_framework import status
import traceback


def handle_error_response(response, error, exception=True) -> Response:
    summary = traceback.StackSummary.extract(traceback.walk_stack(None))

    print(response)

    if response is not None and isinstance(response.data, dict):
        response.data["status_code"] = response.status_code
        response.data["error"] = str(error)

    elif response is not None and isinstance(response.data, list):
        response.data = {
            "status_code": response.status_code,
            "error": str(error),
        }

    else:
        # ------- send invoice to customer mail ----------------
        response = Response(
            {
                "status_code": 503,
                "message": "Service is down or unavailable",
                "error": str(error),
                "traceback": "".join(summary.format()),
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
            exception=exception,
        )

    return response
