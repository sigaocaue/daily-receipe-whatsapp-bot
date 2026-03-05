import logging
import random

from src.application.dtos.recipe_dto import GenerateRecipeDTO
from src.domain.entities.recipe import Recipe
from src.domain.repositories.protein_repository import ProteinRepository
from src.domain.repositories.recipe_repository import RecipeRepository
from src.domain.services.recipe_service import RecipeGeneratorService

logger = logging.getLogger(__name__)


class GenerateRecipeUseCase:
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        protein_repository: ProteinRepository,
        recipe_generator: RecipeGeneratorService,
    ):
        self._recipe_repo = recipe_repository
        self._protein_repo = protein_repository
        self._recipe_generator = recipe_generator

    async def execute(self, dto: GenerateRecipeDTO) -> Recipe:
        if dto.protein_ids:
            proteins = []
            for pid in dto.protein_ids:
                protein = await self._protein_repo.get_by_id(pid)
                if protein:
                    proteins.append(protein)
            if not proteins:
                raise ValueError("No valid proteins found for the given IDs")
        else:
            proteins = await self._protein_repo.get_active()
            if not proteins:
                raise ValueError("No active proteins found in the database")

        selected_protein = random.choice(proteins)
        logger.info("Selected protein: %s", selected_protein.name)

        existing_recipes = await self._recipe_repo.get_all()
        existing_titles = [r.title for r in existing_recipes]

        recipe = await self._recipe_generator.generate_recipe(
            protein_name=selected_protein.name,
            existing_recipe_titles=existing_titles,
        )

        image_url = await self._recipe_generator.fetch_image_url(recipe.title)
        recipe.image_url = image_url
        recipe.protein_ids = [selected_protein.id]

        saved_recipe = await self._recipe_repo.create(recipe)
        logger.info("Recipe generated and saved: %s (id=%s)", saved_recipe.title, saved_recipe.id)
        return saved_recipe
