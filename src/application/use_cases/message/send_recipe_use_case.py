import logging
from dataclasses import dataclass
from uuid import UUID

from src.application.dtos.message_dto import SendResultDTO
from src.domain.entities.message_log import MessageLog
from src.domain.entities.recipe import Recipe
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


@dataclass
class SendRecipeInput:
    recipe_id: UUID | None = None
    title: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    image_url: str | None = None
    save_recipe: bool = False
    phone_number_ids: list[UUID] | None = None


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

    async def _resolve_recipe(
        self, input_data: SendRecipeInput,
    ) -> Recipe:
        if input_data.recipe_id:
            recipe = await self._recipe_repo.get_by_id(input_data.recipe_id)
            if not recipe:
                raise ValueError(
                    f"Recipe with id '{input_data.recipe_id}' not found."
                )
            return recipe

        if input_data.title and input_data.ingredients and input_data.instructions:
            recipe = Recipe(
                title=input_data.title,
                ingredients=input_data.ingredients,
                instructions=input_data.instructions,
                image_url=input_data.image_url,
                ai_generated=False,
            )
            if input_data.save_recipe:
                recipe = await self._recipe_repo.create(recipe)
                logger.info("Custom recipe saved with id: %s", recipe.id)
            return recipe

        last_recipe_ids = await self._message_log_repo.get_last_sent_recipe_ids(
            limit=5,
        )
        logger.info("Last 5 sent recipe IDs: %s", last_recipe_ids)
        recipe = await self._recipe_repo.get_random_excluding(last_recipe_ids)
        if not recipe:
            raise ValueError(
                "No available recipe found. Generate more recipes first."
            )
        return recipe

    async def execute(
        self, input_data: SendRecipeInput | None = None,
    ) -> SendResultDTO:
        input_data = input_data or SendRecipeInput()
        recipe = await self._resolve_recipe(input_data)

        is_custom_unsaved = (
            input_data.title is not None
            and not input_data.save_recipe
            and input_data.recipe_id is None
        )

        if input_data.phone_number_ids:
            active_phones = []
            for phone_id in input_data.phone_number_ids:
                phone = await self._phone_repo.get_by_id(phone_id)
                if phone and phone.active:
                    active_phones.append(phone)
            if not active_phones:
                raise ValueError("No valid active phone numbers found for the given IDs.")
        else:
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

        log_recipe_id = None if is_custom_unsaved else recipe.id

        sent_to = []
        message_log_ids: list[UUID] = []
        for active_phone_entity in active_phones:
            log = MessageLog(
                recipe_id=log_recipe_id,
                phone_number_id=active_phone_entity.id,
                message_content=message_body,
                status="pending",
            )
            try:
                sid = await self._whatsapp.send_message(
                    to=f"whatsapp:{active_phone_entity.phone}",
                    body=message_body,
                    media_url=recipe.image_url,
                )
                log.twilio_message_sid = sid
                log.status = "sent"
                sent_to.append(active_phone_entity.phone)
                logger.info("Message sent to %s (SID: %s)", active_phone_entity.phone, sid)
            except Exception as e:
                log.status = "failed"
                log.error_message = str(e)
                logger.error("Failed to send message to %s: %s", active_phone_entity.phone, e)

            await self._message_log_repo.create(log)

        return SendResultDTO(
            sent_to=sent_to,
            recipe_title=recipe.title,
            recipe_id=log_recipe_id,
            status="sent" if sent_to else "failed",
        )
