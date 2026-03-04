import logging
from uuid import UUID

from src.domain.repositories.recipe_repository import RecipeRepository

logger = logging.getLogger(__name__)


class DeleteRecipeUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self, recipe_id: UUID) -> bool:
        logger.info("Deleting recipe: %s", recipe_id)
        return await self._repository.delete(recipe_id)
