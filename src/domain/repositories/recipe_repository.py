from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.recipe import Recipe


class RecipeRepository(ABC):
    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe: ...

    @abstractmethod
    async def get_by_id(self, recipe_id: UUID) -> Recipe | None: ...

    @abstractmethod
    async def get_all(self) -> list[Recipe]: ...

    @abstractmethod
    async def get_random_excluding(self, exclude_ids: list[UUID]) -> Recipe | None: ...

    @abstractmethod
    async def update(self, recipe_id: UUID, **kwargs) -> Recipe | None: ...

    @abstractmethod
    async def delete(self, recipe_id: UUID) -> bool: ...
