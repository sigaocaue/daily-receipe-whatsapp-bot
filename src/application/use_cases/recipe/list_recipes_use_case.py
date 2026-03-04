from src.domain.entities.recipe import Recipe
from src.domain.repositories.recipe_repository import RecipeRepository


class ListRecipesUseCase:
    def __init__(self, repository: RecipeRepository):
        self._repository = repository

    async def execute(self) -> list[Recipe]:
        return await self._repository.get_all()
