from config.celery import app
from .base import BaseEventTask

# Examples


@app.task(bind=True, base=BaseEventTask)
def send_email(self, payload, event_id, notification):
    """Send email task, inherits failure and success handling from BaseEventTask.

    Args:
        payload (dict): Contains email data (subject, content, from, to, etc.).
        event_id (string): The associated event ID.
        notification (dict): Notification details (if needed for logging).
    """
    # Extract provider from the payload or default to 'zoho'
    email_payload = payload.get("payload", {})
    provider = email_payload.get("provider", "termi")
    email_factory = EmailFactory(provider=provider)

    # Build the email payload using the factory
    email_data = email_factory.build_payload(**email_payload)

    # Send the email
    mail_status = email_factory.send_mail(**email_data)

    return {"status": "SUCCESS", "data": mail_status}


class EmailFactory:
    pass
