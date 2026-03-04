from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.protein_dto import CreateProteinDTO, UpdateProteinDTO
from src.application.use_cases.create_protein_use_case import (
    CreateProteinUseCase,
    DeleteProteinUseCase,
    GetProteinUseCase,
    ListProteinsUseCase,
    UpdateProteinUseCase,
)
from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_protein_repository import (
    SQLAlchemyProteinRepository,
)
from src.presentation.api.schemas.protein_schema import (
    ProteinCreate,
    ProteinResponse,
    ProteinUpdate,
)
from src.presentation.api.schemas.response_schema import ApiResponse
from types import NoneType

router = APIRouter(prefix="/api/v1/proteins", tags=["Proteins"])


def _get_repo(session: AsyncSession) -> SQLAlchemyProteinRepository:
    return SQLAlchemyProteinRepository(session)


@router.post(
    "",
    response_model=ApiResponse[ProteinResponse],
    status_code=201,
    summary="Criar proteína",
    description="Cadastra uma nova proteína disponível para geração de receitas.",
)
async def create_protein(body: ProteinCreate, session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    use_case = CreateProteinUseCase(repo)
    protein = await use_case.execute(CreateProteinDTO(name=body.name, active=body.active))
    return {"data": ProteinResponse.model_validate(protein.__dict__), "message": "Protein created"}


@router.get(
    "",
    response_model=ApiResponse[list[ProteinResponse]],
    summary="Listar proteínas",
    description="Retorna todas as proteínas cadastradas.",
)
async def list_proteins(session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    use_case = ListProteinsUseCase(repo)
    proteins = await use_case.execute()
    return {
        "data": [ProteinResponse.model_validate(p.__dict__) for p in proteins],
        "message": "Proteins listed",
    }


@router.get(
    "/{protein_id}",
    response_model=ApiResponse[ProteinResponse],
    summary="Buscar proteína por ID",
    description="Retorna uma proteína específica pelo seu UUID.",
    responses={404: {"description": "Proteína não encontrada"}},
)
async def get_protein(protein_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    use_case = GetProteinUseCase(repo)
    protein = await use_case.execute(protein_id)
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    return {"data": ProteinResponse.model_validate(protein.__dict__), "message": "Protein found"}


@router.patch(
    "/{protein_id}",
    response_model=ApiResponse[ProteinResponse],
    summary="Atualizar proteína",
    description="Atualiza parcialmente uma proteína existente (nome e/ou status ativo).",
    responses={404: {"description": "Proteína não encontrada"}},
)
async def update_protein(
    protein_id: UUID, body: ProteinUpdate, session: AsyncSession = Depends(get_session)
):
    repo = _get_repo(session)
    use_case = UpdateProteinUseCase(repo)
    protein = await use_case.execute(
        protein_id, UpdateProteinDTO(name=body.name, active=body.active)
    )
    if not protein:
        raise HTTPException(status_code=404, detail="Protein not found")
    return {"data": ProteinResponse.model_validate(protein.__dict__), "message": "Protein updated"}


@router.delete(
    "/{protein_id}",
    response_model=ApiResponse[NoneType],
    summary="Excluir proteína",
    description="Remove permanentemente uma proteína pelo seu UUID.",
    responses={404: {"description": "Proteína não encontrada"}},
)
async def delete_protein(protein_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    use_case = DeleteProteinUseCase(repo)
    deleted = await use_case.execute(protein_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Protein not found")
    return {"data": None, "message": "Protein deleted"}
