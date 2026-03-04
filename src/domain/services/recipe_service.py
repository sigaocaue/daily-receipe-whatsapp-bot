from abc import ABC, abstractmethod

from src.domain.entities.recipe import Recipe


class RecipeGeneratorService(ABC):
    @abstractmethod
    async def generate_recipe(
        self,
        protein_name: str,
        existing_recipe_titles: list[str],
    ) -> Recipe: ...

    @abstractmethod
    async def fetch_image_url(self, query: str) -> str | None: ...
