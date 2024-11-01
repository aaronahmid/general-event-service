from config.celery import app
from .base import BaseEventTask

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.task(bind=True, base=BaseEventTask)
def send_sms(self, payload, event_id, notification):
    pass
