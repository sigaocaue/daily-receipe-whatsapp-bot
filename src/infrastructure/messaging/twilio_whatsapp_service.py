import json
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
        self._content_sid = settings.TWILIO_CONTENT_SID or None

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
        }

        if self._content_sid:
            kwargs["content_sid"] = self._content_sid
            kwargs["content_variables"] = json.dumps({"1": body})
            if media_url:
                kwargs["media_url"] = [media_url]
        else:
            kwargs["body"] = body
            if media_url:
                kwargs["media_url"] = [media_url]

        create_fn = partial(self._client.messages.create, **kwargs)
        message = await to_thread.run_sync(create_fn)
        logger.info("Message sent successfully. SID: %s", message.sid)
        return message.sid
