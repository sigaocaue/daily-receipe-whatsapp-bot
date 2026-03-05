import logging

from src.application.dtos.recipe_dto import ScrapeRecipeDTO
from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository
from src.infrastructure.scraping.tudo_gostoso_scraper import TudoGostosoScraper

logger = logging.getLogger(__name__)


class ScrapeRecipeUseCase:
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        scraper: TudoGostosoScraper,
    ):
        self._recipe_repo = recipe_repository
        self._scraper = scraper

    async def execute(self, dto: ScrapeRecipeDTO) -> Recipe:
        logger.info("Scraping recipe from TudoGostoso (url=%s)", dto.url or "random")
        data = await self._scraper.scrape(dto.url)

        ingredients = "\n".join(data.get("ingredients", []))
        instructions = "\n".join(data.get("preparationSteps", []))
        images = data.get("images", [])

        recipe = Recipe(
            title=data["title"],
            ingredients=ingredients,
            instructions=instructions,
            source_url=data.get("url"),
            image_url=images[0] if images else None,
            source_site="tudogostoso",
            ai_generated=False,
        )

        saved_recipe = await self._recipe_repo.create(recipe)
        logger.info("Scraped recipe saved: %s (id=%s)", saved_recipe.title, saved_recipe.id)
        return saved_recipe
