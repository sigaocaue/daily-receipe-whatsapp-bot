from uuid import UUID

from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository


class GetRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID) -> Recipe | None:
        return await self._repository.get_by_id(recipe_id)
