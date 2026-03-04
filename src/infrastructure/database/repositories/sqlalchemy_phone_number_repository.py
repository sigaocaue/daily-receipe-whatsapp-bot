from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.phone_number import PhoneNumber
from src.domain.repositories.phone_number_repository import PhoneNumberRepository
from src.infrastructure.database.models.phone_number_model import PhoneNumberModel


class SQLAlchemyPhoneNumberRepository(PhoneNumberRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: PhoneNumberModel) -> PhoneNumber:
        return PhoneNumber(
            id=model.id,
            name=model.name,
            phone=model.phone,
            active=model.active,
            created_at=model.created_at,
        )

    async def create(self, phone_number: PhoneNumber) -> PhoneNumber:
        model = PhoneNumberModel(
            id=phone_number.id,
            name=phone_number.name,
            phone=phone_number.phone,
            active=phone_number.active,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, phone_number_id: UUID) -> PhoneNumber | None:
        result = await self._session.get(PhoneNumberModel, phone_number_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[PhoneNumber]:
        result = await self._session.execute(select(PhoneNumberModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_active(self) -> list[PhoneNumber]:
        result = await self._session.execute(
            select(PhoneNumberModel).where(PhoneNumberModel.active.is_(True))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, phone_number_id: UUID, **kwargs) -> PhoneNumber | None:
        model = await self._session.get(PhoneNumberModel, phone_number_id)
        if not model:
            return None
        for key, value in kwargs.items():
            setattr(model, key, value)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, phone_number_id: UUID) -> bool:
        model = await self._session.get(PhoneNumberModel, phone_number_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
