import logging

from src.application.dtos.protein_dto import CreateProteinDTO
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
