from rest_framework import permissions


class AllowedIPsOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        allowed_ips = ["127.0.0.1"]
        client_ip = self.get_client_ip(request)

        return client_ip in allowed_ips

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
