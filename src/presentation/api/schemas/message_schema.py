from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SendRecipeResponse(BaseModel):
    sent_to: list[str]
    recipe: str
    recipe_id: str
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
