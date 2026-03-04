from dataclasses import dataclass
from uuid import UUID
from datetime import datetime


@dataclass
class MessageLogResponseDTO:
    id: UUID
    recipe_id: UUID
    phone_number_id: UUID
    message_content: str
    status: str
    twilio_message_sid: str | None
    error_message: str | None
    sent_at: datetime


@dataclass
class SendResultDTO:
    sent_to: list[str]
    recipe_title: str
    recipe_id: UUID | None
    message_log_ids: list[UUID]
    status: str
