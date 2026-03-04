import logging
from uuid import UUID

from src.application.dtos.recipe_dto import CreateRecipeDTO, UpdateRecipeDTO
from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class CreateRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, dto: CreateRecipeDTO) -> Recipe:
        logger.info("Creating recipe manually: %s", dto.title)
        recipe = Recipe(
            title=dto.title,
            ingredients=dto.ingredients,
            instructions=dto.instructions,
            source_url=dto.source_url,
            image_url=dto.image_url,
            source_site=dto.source_site,
            ai_generated=dto.ai_generated,
            protein_ids=dto.protein_ids or [],
        )
        return await self._repository.create(recipe)


class ListRecipesUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self) -> list[Recipe]:
        return await self._repository.get_all()


class GetRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID) -> Recipe | None:
        return await self._repository.get_by_id(recipe_id)


class UpdateRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID, dto: UpdateRecipeDTO) -> Recipe | None:
        updates = {k: v for k, v in vars(dto).items() if v is not None}
        if not updates:
            return await self._repository.get_by_id(recipe_id)
        return await self._repository.update(recipe_id, **updates)


class DeleteRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID) -> bool:
        logger.info("Deleting recipe: %s", recipe_id)
        return await self._repository.delete(recipe_id)
