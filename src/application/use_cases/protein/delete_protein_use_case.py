import logging
from uuid import UUID

from src.domain.repositories.protein_repository import ProteinRepository

logger = logging.getLogger(__name__)


class DeleteProteinUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self, protein_id: UUID) -> bool:
        logger.info("Deleting protein: %s", protein_id)
        return await self._repository.delete(protein_id)
