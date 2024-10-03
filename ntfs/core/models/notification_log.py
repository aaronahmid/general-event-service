from django.db import models
import uuid


def get_log_body_default():
    return {}


class EventLog(models.Model):

    STATUSES = [
        ("STARTED", "Started"),
        ("FAILURE", "Failure"),
        ("SUCCESS", "Completed"),
        ("RETRY", "Retrying")
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUSES[0][0])
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    body = models.JSONField(serialize=True, null=True, default=get_log_body_default)
    message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class UserNotification(models.Model):
    body = models.JSONField(null=True, serialize=True)
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="notifications"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
