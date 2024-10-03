from rest_framework import serializers
from core.models import User, EventLog


class EventLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventLog
        fields = "__all__"


class EventSerializer(serializers.Serializer):
    ACTIONS = [
        "notify_user",
        "send_sms",
        "send_mail",
    ]
    notification = serializers.JSONField(required=False)
    action = serializers.ChoiceField(choices=ACTIONS, required=True)
    payload = serializers.JSONField(required=True)
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True
    )
    timestamp = serializers.DateTimeField(required=False)
    notify_user = serializers.BooleanField(required=False)
