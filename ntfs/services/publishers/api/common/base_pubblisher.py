from rest_framework.response import Response
from rest_framework import status, permissions, serializers, filters
from rest_framework.views import APIView
import asyncio
from ...tasks.handler import handle_event
from .serializers import EventSerializer, EventLogSerializer

from services.exceptions import handle_error_response
from services.exceptions import exception_handler
from .permissions import AllowedIPsOnly

from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async

from core.models import EventLog, User


class BaseEventPublisherView(APIView):
    http_method_names = ["post"]
    permission_classes = [permissions.AllowAny]  # [AllowedIPsOnly]

    @sync_to_async
    def handle_error(self, error, context="An error has occurred"):
        response = exception_handler(error, context)
        return handle_error_response(response, error)

    @sync_to_async
    def validate_data(self, data):
        data = EventSerializer(data=data)
        data.is_valid(raise_exception=True)

    @sync_to_async
    def create_event_log(self, user_id, data):
        print("creating event log")
        user = User.objects.get(user_id=user_id)
        event = EventLog.objects.create(user=user, body=data)
        event.save()
        return event

    @sync_to_async
    def create_user_notification(self, user):
        pass

    @async_to_sync
    async def post(self, request, *args, **kwargs):
        try:

            await self.validate_data(request.data)

            data = request.data
            user = data["user"]
            event = await self.create_event_log(user, data)

        except Exception as error:
            return await self.handle_error(error)

        # Process the event asynchronously
        # asyncio.create_task(handle_event(event))
        handle_event.apply_async(args=[event.id])
        return Response(
            data={"status": 200, "message": "Event published"},
            status=status.HTTP_200_OK,
        )

    # @database_sync_to_async
    # async def process_event(self, user_id, action, payload):
    #     await handle_event(user_id, action, payload)
