# app/consumers/base_consumer.py
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.exceptions import StopConsumer

# from aioredis import from_url as redis_from_url
# import os
from config.settings import getvar

# from services.utils import Cache
# from asgiref.sync import sync_to_async, async_to_sync
# from django.core.cache import caches
# from channels import Group
from services.exceptions import handle_error_response, exception_handler

# cache = Cache(timeout=84000)

REDIS_URL = getvar("REDIS_URI")


class BaseConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """handles what happens when user connects
        Create a group for a user and adds the user to that group channel
        """
        # When a WebSocket client connects to this consumer,
        # accept the connection.
        self.user = self.scope["user"]
        self.group_name = f"{self.user.id}_group"

        if self.user.is_authenticated:
            try:
                await self.channel_layer.group_add(self.group_name, self.channel_name)
                await self.accept()
            except Exception as error:
                response = exception_handler(error, "an error occurred")
                return handle_error_response(response, error)
        else:
            await self.close()

    async def disconnect(self, close_code):
        # When a WebSocket client disconnects, you can perform any cleanup here,
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        raise StopConsumer()

    async def send_exit_signal(self, event):
        await self.close()

    # Broadcast exit signal to all consumers
    async def shutdown_consumers(self):
        await self.channel_layer.group_send(
            self.group_name, {"type": "send_exit_signal"}
        )

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        try:
            return await super().receive(text_data, bytes_data, **kwargs)
        except Exception as error:
            response = exception_handler(error, "an error occurred")
            return handle_error_response(response, error)

    async def handle_action(self, action, payload):
        raise NotImplementedError("This method needs to be implemented by subclasses")

    async def send_notification(self, message):
        try:
            await self.send_json(message)
        except Exception as error:
            response = exception_handler(error, "an error occurred")
            return handle_error_response(response, error)

    # @sync_to_async
    # def add_user_to_cache(self):
    #     # redis = redis_from_url(REDIS_URL)
    #     # await redis.sadd(f"user_{self.user_id}", self.channel_name)
    #     # await redis.close()
    #     print(self.user_id, "USER")
    #     print(f"user_ch_{self.user_id}")
    #     user_channels = caches["default"].get(f"user_ch_{self.user_id}")
    #     if user_channels:
    #         user_channels = []
    #         print("here", user_channels)
    #         user_channels.append(self.channel_name)
    #         caches["default"].delete(f"user_ch_{self.user_id}")
    #         caches["default"].set(f"user_ch_{self.user_id}", user_channels)
    #     else:
    #         user_channels = []
    #         user_channels.append(self.channel_name)
    #         caches["default"].set(f"user_ch_{self.user_id}", user_channels)

    #     # print(cache.get(f"user_ch_{self.user_id}"))

    # @sync_to_async
    # def remove_user_from_cache(self):
    #     caches["default"].delete(f"user_ch_{self.user_id}")
