from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.message.send_recipe_use_case import SendRecipeInput, SendRecipeUseCase
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
from src.presentation.api.schemas.message_schema import (
    MessageLogResponse,
    SendRecipeRequest,
    SendRecipeResponse,
)
from src.presentation.api.schemas.response_schema import ApiResponse

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.post(
    "/send",
    response_model=ApiResponse[SendRecipeResponse],
    summary="Enviar receita via WhatsApp",
    description=(
        "Envia uma receita via WhatsApp. Pode-se: (1) enviar sem body para selecionar "
        "uma receita aleatória, (2) informar recipe_id para usar uma receita existente, "
        "ou (3) informar title, ingredients e instructions para enviar uma receita "
        "personalizada, opcionalmente salvando-a no banco de dados."
    ),
    responses={404: {"description": "Nenhuma receita ou número ativo encontrado"}},
)
async def send_recipe(
    body: SendRecipeRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    recipe_repo = SQLAlchemyRecipeRepository(session)
    phone_repo = SQLAlchemyPhoneNumberRepository(session)
    log_repo = SQLAlchemyMessageLogRepository(session)
    whatsapp = TwilioWhatsAppService()

    input_data = None
    if body:
        input_data = SendRecipeInput(
            recipe_id=body.recipe_id,
            title=body.title,
            ingredients=body.ingredients,
            instructions=body.instructions,
            image_url=body.image_url,
            save_recipe=body.save_recipe,
            phone_number_ids=body.phone_number_ids,
        )

    use_case = SendRecipeUseCase(recipe_repo, phone_repo, log_repo, whatsapp)
    try:
        result = await use_case.execute(input_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {
        "data": {
            "sent_to": result.sent_to,
            "recipe": result.recipe_title,
            "recipe_id": str(result.recipe_id) if result.recipe_id else None,
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
