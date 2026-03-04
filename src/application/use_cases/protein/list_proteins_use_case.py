from src.domain.entities.protein import Protein
from src.domain.repositories.protein_repository import ProteinRepository


class ListProteinsUseCase:
    def __init__(self, repository: ProteinRepository):
        self._repository = repository

    async def execute(self) -> list[Protein]:
        return await self._repository.get_all()
