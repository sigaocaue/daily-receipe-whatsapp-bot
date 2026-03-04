from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.send_recipe_use_case import SendRecipeUseCase
from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_message_log_repository import (
    SQLAlchemyMessageLogRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_phone_number_repository import (
    SQLAlchemyPhoneNumberRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)
from src.infrastructure.messaging.twilio_whatsapp_service import TwilioWhatsAppService
from src.presentation.api.schemas.message_schema import MessageLogResponse, SendRecipeResponse
from src.presentation.api.schemas.response_schema import ApiResponse

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.post(
    "/send",
    response_model=ApiResponse[SendRecipeResponse],
    summary="Enviar receita via WhatsApp",
    description=(
        "Seleciona uma receita (evitando as últimas 5 enviadas) e envia para todos os "
        "números de telefone ativos via WhatsApp usando a API do Twilio."
    ),
    responses={404: {"description": "Nenhuma receita ou número ativo encontrado"}},
)
async def send_recipe(session: AsyncSession = Depends(get_session)):
    recipe_repo = SQLAlchemyRecipeRepository(session)
    phone_repo = SQLAlchemyPhoneNumberRepository(session)
    log_repo = SQLAlchemyMessageLogRepository(session)
    whatsapp = TwilioWhatsAppService()

    use_case = SendRecipeUseCase(recipe_repo, phone_repo, log_repo, whatsapp)
    try:
        result = await use_case.execute()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "data": {
            "sent_to": result.sent_to,
            "recipe": result.recipe_title,
            "recipe_id": str(result.recipe_id),
            "status": result.status,
        },
        "message": "Recipe sent via WhatsApp",
    }


@router.get(
    "/logs",
    response_model=ApiResponse[list[MessageLogResponse]],
    summary="Listar histórico de mensagens",
    description="Retorna o histórico completo de mensagens enviadas via WhatsApp.",
)
async def list_logs(session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyMessageLogRepository(session)
    logs = await repo.get_all()
    return {
        "data": [
            {
                "id": str(log.id),
                "recipe_id": str(log.recipe_id),
                "phone_number_id": str(log.phone_number_id),
                "message_content": log.message_content,
                "status": log.status,
                "twilio_message_sid": log.twilio_message_sid,
                "error_message": log.error_message,
                "sent_at": log.sent_at.isoformat(),
            }
            for log in logs
        ],
        "message": "Message logs listed",
    }


@router.get(
    "/logs/{log_id}",
    response_model=ApiResponse[MessageLogResponse],
    summary="Buscar log de mensagem por ID",
    description="Retorna os detalhes de um log de mensagem específico pelo seu UUID.",
    responses={404: {"description": "Log de mensagem não encontrado"}},
)
async def get_log(log_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyMessageLogRepository(session)
    log = await repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Message log not found")
    return {
        "data": {
            "id": str(log.id),
            "recipe_id": str(log.recipe_id),
            "phone_number_id": str(log.phone_number_id),
            "message_content": log.message_content,
            "status": log.status,
            "twilio_message_sid": log.twilio_message_sid,
            "error_message": log.error_message,
            "sent_at": log.sent_at.isoformat(),
        },
        "message": "Message log found",
    }
