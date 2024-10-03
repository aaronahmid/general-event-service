from services.subscribers.common.base_consumer import BaseConsumer
from django.urls import path

ws_urlpatterns = [
    path("ws/subscribe/", BaseConsumer.as_asgi())
]
