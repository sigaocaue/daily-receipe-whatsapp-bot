import logging

from src.application.dtos.message_dto import SendResultDTO
from src.domain.entities.message_log import MessageLog
from src.domain.repositories.message_log_repository import MessageLogRepository
from src.domain.repositories.phone_number_repository import PhoneNumberRepository
from src.domain.repositories.recipe_repository import RecipeRepository
from src.domain.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

MESSAGE_TEMPLATE = """Bom dia, meu amor! 💕

Hoje preparei uma receita especial com *{protein}* para você:

🍽️ *{title}* (fonte: {source_site})

Ingredientes:
{ingredients}

Modo de preparo:
{instructions}

Beijos e bom apetite! 🥘
Para mais detalhes: {source_url}"""


class SendRecipeUseCase:
    def __init__(
        self,
        recipe_repository: RecipeRepository,
        phone_number_repository: PhoneNumberRepository,
        message_log_repository: MessageLogRepository,
        whatsapp_service: WhatsAppService,
    ):
        self._recipe_repo = recipe_repository
        self._phone_repo = phone_number_repository
        self._message_log_repo = message_log_repository
        self._whatsapp = whatsapp_service

    async def execute(self) -> SendResultDTO:
        last_recipe_ids = await self._message_log_repo.get_last_sent_recipe_ids(limit=5)
        logger.info("Last 5 sent recipe IDs: %s", last_recipe_ids)

        recipe = await self._recipe_repo.get_random_excluding(last_recipe_ids)
        if not recipe:
            raise ValueError("No available recipe found. Generate more recipes first.")

        active_phones = await self._phone_repo.get_active()
        if not active_phones:
            raise ValueError("No active phone numbers found.")

        protein_name = "proteína especial"
        message_body = MESSAGE_TEMPLATE.format(
            protein=protein_name,
            title=recipe.title,
            source_site=recipe.source_site or "Internet",
            ingredients=recipe.ingredients,
            instructions=recipe.instructions,
            source_url=recipe.source_url or "",
        )

        sent_to = []
        for phone in active_phones:
            log = MessageLog(
                recipe_id=recipe.id,
                phone_number_id=phone.id,
                message_content=message_body,
                status="pending",
            )
            try:
                sid = await self._whatsapp.send_message(
                    to=f"whatsapp:{phone.phone}",
                    body=message_body,
                    media_url=recipe.image_url,
                )
                log.twilio_message_sid = sid
                log.status = "sent"
                sent_to.append(phone.phone)
                logger.info("Message sent to %s (SID: %s)", phone.phone, sid)
            except Exception as e:
                log.status = "failed"
                log.error_message = str(e)
                logger.error("Failed to send message to %s: %s", phone.phone, e)

            await self._message_log_repo.create(log)

        return SendResultDTO(
            sent_to=sent_to,
            recipe_title=recipe.title,
            recipe_id=recipe.id,
            status="sent" if sent_to else "failed",
        )
