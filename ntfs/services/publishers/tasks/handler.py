# app/event_handler.py
from services.publishers.tasks import notify_user_task, send_email, send_sms
from core.models import EventLog
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)
from config.celery import app


@app.task(max_retries=5, default_retry_delay=30)
def handle_event(event_id):
    # initialize event factory
    event = EventLog.objects.get(id=event_id)
    print("Handling event")
    factory = EventFactory(event)
    factory.perform_action()


class EventFactory:
    _event: EventLog = None
    action: str = ""
    payload: dict = {}
    user_id = ""

    # Actions map to background tasks
    # so you can create as many task and then
    # add then here
    ACTIONS = {
        "notify_user": notify_user_task,
        "send_mail": send_email,
        "send_sms": send_sms
    }

    def __init__(self, event: EventLog):
        print("initializing factory")
        self._event = event
        event_body = self._event.body
        self.user_id = self._event.user.id
        self.action = event_body.get("action", "")
        self.payload = event_body

    def load_action(self, action):
        logger.debug("loading action...")
        return self.ACTIONS[action]

    def perform_action(self):
        print("performing action...")
        action = self.load_action(self.action)
        notification = self._event.body.get("notification", {})
        action.delay(self.payload, self._event.id, notification)
