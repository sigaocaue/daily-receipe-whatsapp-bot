from uuid import UUID

from src.application.dtos.protein_dto import UpdateProteinDTO
from src.domain.entities.protein import Protein
from src.domain.repositories.protein_repository import ProteinRepository


class UpdateProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID, dto: UpdateProteinDTO) -> Protein | None:
        updates = {k: v for k, v in vars(dto).items() if v is not None}
        if not updates:
            return await self._repository.get_by_id(protein_id)
        return await self._repository.update(protein_id, **updates)
