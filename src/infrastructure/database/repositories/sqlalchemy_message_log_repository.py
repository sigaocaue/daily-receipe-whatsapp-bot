from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.message_log import MessageLog
from src.domain.repositories.message_log_repository import MessageLogRepository
from src.infrastructure.database.models.message_log_model import MessageLogModel


class SQLAlchemyMessageLogRepository(MessageLogRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: MessageLogModel) -> MessageLog:
        return MessageLog(
            id=model.id,
            recipe_id=model.recipe_id,
            phone_number_id=model.phone_number_id,
            message_content=model.message_content,
            status=model.status,
            twilio_message_sid=model.twilio_message_sid,
            error_message=model.error_message,
            sent_at=model.sent_at,
        )

    async def create(self, message_log: MessageLog) -> MessageLog:
        model = MessageLogModel(
            id=message_log.id,
            recipe_id=message_log.recipe_id,
            phone_number_id=message_log.phone_number_id,
            message_content=message_log.message_content,
            status=message_log.status,
            twilio_message_sid=message_log.twilio_message_sid,
            error_message=message_log.error_message,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, log_id: UUID) -> MessageLog | None:
        result = await self._session.get(MessageLogModel, log_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[MessageLog]:
        result = await self._session.execute(
            select(MessageLogModel).order_by(MessageLogModel.sent_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_last_sent_recipe_ids(self, limit: int = 5) -> list[UUID]:
        result = await self._session.execute(
            select(MessageLogModel.recipe_id)
            .where(MessageLogModel.status == "sent")
            .order_by(MessageLogModel.sent_at.desc())
            .distinct()
            .limit(limit)
        )
        return list(result.scalars().all())
