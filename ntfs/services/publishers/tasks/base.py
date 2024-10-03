from config.celery import app
from celery.utils.log import get_task_logger
from core.models import EventLog
import traceback
from core.models import UserNotification
import msgpack
from celery import current_app


logger = get_task_logger(__name__)


def notify_user(user_id, payload, save_notification=False):
    try:
        if save_notification:
            UserNotification.objects.create(user=user_id, body=payload)
    except Exception as error:
        logger.exception(f"Error in notify_user: {error}")
        return f"Error: {error}"

    try:
        logger.debug(f"Starting notify_user for user {user_id} with action")
        channel = f"{user_id}_group"
        logger.debug(f"Sending message to channel: {channel}")
        data = {"type": "send_notification", "data": payload}

        with current_app.producer_pool.acquire(block=True) as producer:
            producer.publish(
                msgpack.packb(
                    {
                        "__asgi_group__": channel,
                        **data,
                    }
                ),
                exchange="groups",  # The RabbitMQ exchange for websocket groups
                content_encoding="binary",
                routing_key=channel,  # The group that will receive the message
                retry=False,  # Channel Layer at-most-once semantics
            )

        logger.debug("Notification sent successfully")
        return "Notification sent successfully"
    except Exception as error:
        logger.exception(f"Error in notify_user: {error}")
        return f"Error: {error}"


class BaseEventTask(app.Task):
    autoretry_for = (Exception,)
    retry_backoff = 5  # retry after 5 seconds
    max_retries = 3  # max retries before failure
    logger = logger

    def update_event_status(self, event_id, status, message=None):
        """
        Update the event log with the current status of the task.
        """
        try:
            event = EventLog.objects.get(id=event_id)
            event.status = status
            event.message = message
            event.save()
        except EventLog.DoesNotExist:
            self.logger.error(f"Event with ID {event_id} not found")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Handle task failure, including retries and updating the event status.
        """
        user_id = args[0].get("user")
        event_id = str(args[1])
        notification = args[2]
        notify_on_failure = notification.get("notify_on_failure", False)
        save_notification = notification.get("save_notification", False)
        failure_message = notification.get("failure_message", "event failed")

        # Capture exception details
        exc_type = type(exc).__name__
        exc_message = str(exc)
        exc_traceback = traceback.format_exc()

        # Log the error
        self.logger.error(f"Task {task_id} failed: {exc_type} - {exc_message}")
        self.logger.error(f"Traceback: {exc_traceback}")

        # Check if retry limit is reached
        retries = self.request.retries
        if retries < self.max_retries:
            self.logger.info(f"Retrying task {task_id}, attempt {retries + 1}")
        else:
            # Update event status to 'FAILURE'
            self.update_event_status(event_id, "FAILURE", f"{exc_type}: {exc_message}")

            # Notify the user if failure notifications are enabled
            if notify_on_failure and user_id:
                notify_user(
                    user_id,
                    {
                        "status": "FAILURE",
                        "message": f"{failure_message} failed after {retries} retries due to: {exc_type} - {exc_message}",
                    },
                    save_notification,
                )

        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """
        Handle task success, including updating the event status and notifying the user.
        """
        logger.info(args)
        user_id = args[0].get("user")
        event_id = str(args[1])
        notification = args[2]
        notify_on_success = notification.get("notify_on_success", False)
        save_notification = notification.get("save_notification", False)
        success_message = notification.get("success_message", "event completed")
        self.logger.info(f"user id: {user_id}")
        self.logger.info(f"notify: {notify_on_success}")

        # Update event status to 'SUCCESS'
        self.update_event_status(event_id, "SUCCESS", success_message)

        # Notify the user if success notifications are enabled
        if notify_on_success and user_id:
            notify_user(
                user_id,
                {
                    "status": "SUCCESS",
                    "message": success_message,
                },
                save_notification,
            )

        super().on_success(retval, task_id, args, kwargs)

    def run(self, *args, **kwargs):
        """
        Override this method in subclasses to define task logic.
        """
        raise NotImplementedError("Subclasses should implement this!")


@app.task(bind=True, base=BaseEventTask)
def notify_user_task(self, payload, event_id, notification: dict):
    message = payload.get("payload", {})
    user = payload.get("user", "")
    save_notification = notification.get("save_notification", True)
    notify_user(user, message, save_notification)
