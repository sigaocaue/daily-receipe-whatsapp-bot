import logging
from functools import partial

from anyio import to_thread
from twilio.rest import Client

from config import settings
from src.domain.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class TwilioWhatsAppService(WhatsAppService):
    def __init__(self):
        self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self._from_number = settings.TWILIO_WHATSAPP_FROM

    async def send_message(
        self,
        to: str,
        body: str,
        media_url: str | None = None,
    ) -> str:
        logger.info("Sending WhatsApp message to %s", to)
        kwargs = {
            "from_": self._from_number,
            "to": to,
            "body": body,
        }
        if media_url:
            kwargs["media_url"] = [media_url]

        create_fn = partial(self._client.messages.create, **kwargs)
        message = await to_thread.run_sync(create_fn)
        logger.info("Message sent successfully. SID: %s", message.sid)
        return message.sid
