from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "message": "success!",
                "code": 200,
                "payload": data,
                "meta": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": self.page.paginator.count,
                    "page_size": self.page.paginator.per_page,
                },
            }
        )

    def paginate_queryset(self, queryset, request, view=None):
        # Check if the page_size parameter is provided in the request
        page_size = request.query_params.get(self.page_size_query_param)

        if page_size == "all":
            # If "page_size" is set to "all," return all data without pagination
            return None

        try:
            return super().paginate_queryset(queryset, request, view)
        except ValidationError as error:
            raise error
