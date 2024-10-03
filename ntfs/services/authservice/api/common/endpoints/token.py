from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from oauth2_provider.views.base import TokenView


class TokenAPIBaseClass(TokenView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 400:
            return JsonResponse({"detail": _("Invalid credentials given.")}, status=400)
        return response
