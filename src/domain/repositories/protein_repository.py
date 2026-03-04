from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.protein import Protein


class ProteinRepository(ABC):
    @abstractmethod
    async def create(self, protein: Protein) -> Protein: ...

    @abstractmethod
    async def get_by_id(self, protein_id: UUID) -> Protein | None: ...

    @abstractmethod
    async def get_all(self) -> list[Protein]: ...

    @abstractmethod
    async def get_active(self) -> list[Protein]: ...

    @abstractmethod
    async def update(self, protein_id: UUID, **kwargs) -> Protein | None: ...

    @abstractmethod
    async def delete(self, protein_id: UUID) -> bool: ...
