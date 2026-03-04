from uuid import UUID

from src.domain.entities.protein import Protein
from src.domain.repositories.protein_repository import ProteinRepository


class GetProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID) -> Protein | None:
        return await self._repository.get_by_id(protein_id)
