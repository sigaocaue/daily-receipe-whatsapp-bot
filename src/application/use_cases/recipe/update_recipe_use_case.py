from uuid import UUID

from src.application.dtos.recipe_dto import UpdateRecipeDTO
from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository


class UpdateRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID, dto: UpdateRecipeDTO) -> Recipe | None:
        updates = {k: v for k, v in vars(dto).items() if v is not None}
        if not updates:
            return await self._repository.get_by_id(recipe_id)
        return await self._repository.update(recipe_id, **updates)
