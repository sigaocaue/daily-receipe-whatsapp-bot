from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.message_log import MessageLog


class MessageLogRepository(ABC):
    @abstractmethod
    async def create(self, message_log: MessageLog) -> MessageLog: ...

    @abstractmethod
    async def get_by_id(self, log_id: UUID) -> MessageLog | None: ...

    @abstractmethod
    async def get_all(self) -> list[MessageLog]: ...

    @abstractmethod
    async def get_last_sent_recipe_ids(self, limit: int = 5) -> list[UUID]: ...
