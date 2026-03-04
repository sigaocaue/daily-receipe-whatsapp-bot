import logging

from src.application.dtos.recipe_dto import CreateRecipeDTO
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
