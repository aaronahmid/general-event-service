# from twilio.rest import Client
# from config.settings import (
#     TWILIO_ACCOUNT_SID,
#     TWILIO_AUTH_TOKEN,
#     TWILIO_SENDER,
#     TERMI_API_KEY,
# )
# import logging
# from services.exceptions import (
#     APIClientException,
#     exception_handler,
#     handle_error_response,
# )
# from services.clients import APIClient
from config.celery import app
from .base import BaseEventTask

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)


@app.task(bind=True, base=BaseEventTask)
def send_sms(self, payload, event_id, notification):
    pass
#     sms_payload = payload.get("payload", {})
#     provider = payload.get("provider", "Termi")
#     to = sms_payload.get("phone", "")
#     message = sms_payload.get("message", "")

#     status = SMSFactory.send_sms(provider=provider, phone=to, message=message)

#     if status is True:
#         return {"status": "SUCCESS", "data": "sms sent"}

#     return {"status": "FAILURE", "data": "sms failed"}


# class Twilio:

#     @staticmethod
#     def send_sms(message, phone):
#         try:
#             client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#             client.messages.create(body=message, from_=TWILIO_SENDER, to=phone)

#         except Exception as error:
#             error_response = exception_handler(error, "An error occurred")
#             response = handle_error_response(error_response, error)
#             return {"status": "FAILED", "data": response.json()}

#         return True


# class Termi:

#     @staticmethod
#     def send_sms(message, phone):
#         try:
#             client = APIClient("https://api.ng.termii.com", "API_KEY")
#             payload = {
#                 "from": "AAJ Express",
#                 "type": "plain",
#                 "channel": "generic",
#                 "api_key": TERMI_API_KEY,
#             }
#             headers = {
#                 "Content-Type": "application/json",
#             }

#             # format phone
#             if phone.startswith("0"):
#                 phone = "+234" + phone[1:]

#             payload["sms"] = message
#             payload["to"] = phone

#             response = client.request(
#                 "post", "/api/sms/send", headers=headers, data=payload
#             )

#         except Exception as error:
#             error_response = exception_handler(error, "An error occurred")
#             response = handle_error_response(error_response, error)
#             return {"status": "FAILED", "data": response.json()}

#         if response.status_code != 200:
#             raise APIClientException(
#                 client.json,
#                 code=client.status_code,
#             )
#         else:
#             return True


# class SMSFactory:

#     PROVIDERS = {"Twilio": Twilio, "Termi": Termi}

#     def get_provider(self, provider: str):
#         provider_name = provider.title()
#         return self.get_provider(provider_name)

#     def send_sms(self, **kwargs):
#         provider = self.get_provider(kwargs.get("provider_name"))
#         status = provider.send_sms(kwargs.get("message"), kwargs.get("phone"))
#         return status
