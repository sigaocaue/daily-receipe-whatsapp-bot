from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.phone_number import PhoneNumber
from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_phone_number_repository import (
    SQLAlchemyPhoneNumberRepository,
)
from src.presentation.api.schemas.phone_number_schema import (
    PhoneNumberCreate,
    PhoneNumberResponse,
    PhoneNumberUpdate,
)
from src.presentation.api.schemas.response_schema import ApiResponse

router = APIRouter(prefix="/api/v1/phone-numbers", tags=["Phone Numbers"])


def _get_repo(session: AsyncSession) -> SQLAlchemyPhoneNumberRepository:
    return SQLAlchemyPhoneNumberRepository(session)


@router.post(
    "",
    response_model=ApiResponse[PhoneNumberResponse],
    status_code=201,
    summary="Cadastrar número de telefone",
    description="Adiciona um novo número de telefone como destinatário de receitas via WhatsApp.",
)
async def create_phone_number(
    body: PhoneNumberCreate, session: AsyncSession = Depends(get_session)
):
    repo = _get_repo(session)
    phone = PhoneNumber(name=body.name, phone=body.phone, active=body.active)
    created = await repo.create(phone)
    return {
        "data": PhoneNumberResponse.model_validate(created.__dict__),
        "message": "Phone number created",
    }


@router.get(
    "",
    response_model=ApiResponse[list[PhoneNumberResponse]],
    summary="Listar números de telefone",
    description="Retorna todos os números de telefone cadastrados.",
)
async def list_phone_numbers(session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    phones = await repo.get_all()
    return {
        "data": [PhoneNumberResponse.model_validate(p.__dict__) for p in phones],
        "message": "Phone numbers listed",
    }


@router.get(
    "/{phone_id}",
    response_model=ApiResponse[PhoneNumberResponse],
    summary="Buscar número por ID",
    description="Retorna um número de telefone específico pelo seu UUID.",
    responses={404: {"description": "Número de telefone não encontrado"}},
)
async def get_phone_number(phone_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    phone = await repo.get_by_id(phone_id)
    if not phone:
        raise HTTPException(status_code=404, detail="Phone number not found")
    return {
        "data": PhoneNumberResponse.model_validate(phone.__dict__),
        "message": "Phone number found",
    }


@router.patch(
    "/{phone_id}",
    response_model=ApiResponse[PhoneNumberResponse],
    summary="Atualizar número de telefone",
    description="Atualiza parcialmente um número de telefone (nome, número e/ou status ativo).",
    responses={404: {"description": "Número de telefone não encontrado"}},
)
async def update_phone_number(
    phone_id: UUID, body: PhoneNumberUpdate, session: AsyncSession = Depends(get_session)
):
    repo = _get_repo(session)
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        phone = await repo.get_by_id(phone_id)
    else:
        phone = await repo.update(phone_id, **updates)
    if not phone:
        raise HTTPException(status_code=404, detail="Phone number not found")
    return {
        "data": PhoneNumberResponse.model_validate(phone.__dict__),
        "message": "Phone number updated",
    }


@router.delete(
    "/{phone_id}",
    response_model=ApiResponse[None],
    summary="Excluir número de telefone",
    description="Remove permanentemente um número de telefone pelo seu UUID.",
    responses={404: {"description": "Número de telefone não encontrado"}},
)
async def delete_phone_number(phone_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = _get_repo(session)
    deleted = await repo.delete(phone_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Phone number not found")
    return {"data": None, "message": "Phone number deleted"}
