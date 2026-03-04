from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.protein import Protein
from src.domain.repositories.protein_repository import ProteinRepository
from src.infrastructure.database.models.protein_model import ProteinModel


class SQLAlchemyProteinRepository(ProteinRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: ProteinModel) -> Protein:
        return Protein(
            id=model.id,
            name=model.name,
            active=model.active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, protein: Protein) -> Protein:
        model = ProteinModel(
            id=protein.id,
            name=protein.name,
            active=protein.active,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, protein_id: UUID) -> Protein | None:
        result = await self._session.get(ProteinModel, protein_id)
        return self._to_entity(result) if result else None

    async def get_all(self) -> list[Protein]:
        result = await self._session.execute(select(ProteinModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_active(self) -> list[Protein]:
        result = await self._session.execute(
            select(ProteinModel).where(ProteinModel.active.is_(True))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, protein_id: UUID, **kwargs) -> Protein | None:
        model = await self._session.get(ProteinModel, protein_id)
        if not model:
            return None
        for key, value in kwargs.items():
            setattr(model, key, value)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, protein_id: UUID) -> bool:
        model = await self._session.get(ProteinModel, protein_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
