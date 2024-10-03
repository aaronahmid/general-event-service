from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from services.subscribers.ws_urls import ws_urlpatterns
from services.subscribers.middleware import TokenAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            TokenAuthMiddleware(URLRouter(ws_urlpatterns))
        )
    }
)
