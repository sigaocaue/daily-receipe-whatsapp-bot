from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SendRecipeRequest(BaseModel):
    recipe_id: UUID | None = Field(
        default=None,
        description="ID de uma receita existente no banco de dados para enviar.",
    )
    title: str | None = Field(
        default=None,
        description="Título da receita personalizada.",
    )
    ingredients: str | None = Field(
        default=None,
        description="Ingredientes da receita personalizada.",
    )
    instructions: str | None = Field(
        default=None,
        description="Modo de preparo da receita personalizada.",
    )
    image_url: str | None = Field(
        default=None,
        description="URL da imagem da receita personalizada.",
    )
    save_recipe: bool = Field(
        default=False,
        description="Se deve salvar a receita personalizada no banco de dados.",
    )
    phone_number_ids: list[UUID] | None = Field(
        default=None,
        description="Lista de IDs de números de telefone para enviar. Se não informado, envia para todos os ativos.",
    )


class SendRecipeResponse(BaseModel):
    sent_to: list[str]
    recipe: str
    recipe_id: str | None
    status: str


class MessageLogResponse(BaseModel):
    id: str
    recipe_id: str
    phone_number_id: str
    message_content: str
    status: str
    twilio_message_sid: str | None
    error_message: str | None
    sent_at: datetime
