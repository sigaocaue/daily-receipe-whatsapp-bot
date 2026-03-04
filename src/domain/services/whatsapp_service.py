from abc import ABC, abstractmethod


class WhatsAppService(ABC):
    @abstractmethod
    async def send_message(
        self,
        to: str,
        body: str,
        media_url: str | None = None,
    ) -> str: ...
