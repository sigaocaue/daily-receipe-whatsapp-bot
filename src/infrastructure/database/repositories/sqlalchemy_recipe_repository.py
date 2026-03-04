from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository
from src.infrastructure.database.models.protein_model import ProteinModel
from src.infrastructure.database.models.recipe_model import RecipeModel


class SQLAlchemyRecipeRepository(RecipeRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: RecipeModel) -> Recipe:
        return Recipe(
            id=model.id,
            title=model.title,
            ingredients=model.ingredients,
            instructions=model.instructions,
            source_url=model.source_url,
            image_url=model.image_url,
            source_site=model.source_site,
            ai_generated=model.ai_generated,
            protein_ids=[p.id for p in model.proteins] if model.proteins else [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, recipe: Recipe) -> Recipe:
        model = RecipeModel(
            id=recipe.id,
            title=recipe.title,
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            source_url=recipe.source_url,
            image_url=recipe.image_url,
            source_site=recipe.source_site,
            ai_generated=recipe.ai_generated,
        )
        if recipe.protein_ids:
            for pid in recipe.protein_ids:
                protein = await self._session.get(ProteinModel, pid)
                if protein:
                    model.proteins.append(protein)

        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model, ["proteins"])
        return self._to_entity(model)

    async def get_by_id(self, recipe_id: UUID) -> Recipe | None:
        result = await self._session.execute(
            select(RecipeModel)
            .options(selectinload(RecipeModel.proteins))
            .where(RecipeModel.id == recipe_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_all(self) -> list[Recipe]:
        result = await self._session.execute(
            select(RecipeModel).options(selectinload(RecipeModel.proteins))
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_random_excluding(self, exclude_ids: list[UUID]) -> Recipe | None:
        query = select(RecipeModel).options(selectinload(RecipeModel.proteins))
        if exclude_ids:
            query = query.where(RecipeModel.id.notin_(exclude_ids))
        query = query.order_by(func.random()).limit(1)
        result = await self._session.execute(query)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, recipe_id: UUID, **kwargs) -> Recipe | None:
        result = await self._session.execute(
            select(RecipeModel)
            .options(selectinload(RecipeModel.proteins))
            .where(RecipeModel.id == recipe_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        for key, value in kwargs.items():
            setattr(model, key, value)
        await self._session.commit()
        await self._session.refresh(model, ["proteins"])
        return self._to_entity(model)

    async def delete(self, recipe_id: UUID) -> bool:
        model = await self._session.get(RecipeModel, recipe_id)
        if not model:
            return False
        await self._session.delete(model)
        await self._session.commit()
        return True
