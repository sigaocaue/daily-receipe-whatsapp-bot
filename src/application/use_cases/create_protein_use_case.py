import logging
from uuid import UUID

from src.application.dtos.protein_dto import CreateProteinDTO, UpdateProteinDTO
from src.domain.entities.protein import Protein
from src.domain.repositories.protein_repository import ProteinRepository

logger = logging.getLogger(__name__)


class CreateProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, dto: CreateProteinDTO) -> Protein:
        logger.info("Creating protein: %s", dto.name)
        protein = Protein(name=dto.name, active=dto.active)
        return await self._repository.create(protein)


class ListProteinsUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self) -> list[Protein]:
        return await self._repository.get_all()


class GetProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID) -> Protein | None:
        return await self._repository.get_by_id(protein_id)


class UpdateProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID, dto: UpdateProteinDTO) -> Protein | None:
        updates = {k: v for k, v in vars(dto).items() if v is not None}
        if not updates:
            return await self._repository.get_by_id(protein_id)
        return await self._repository.update(protein_id, **updates)


class DeleteProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID) -> bool:
        logger.info("Deleting protein: %s", protein_id)
        return await self._repository.delete(protein_id)
