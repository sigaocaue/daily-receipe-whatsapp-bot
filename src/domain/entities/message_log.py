from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class MessageLog:
    recipe_id: UUID
    phone_number_id: UUID
    message_content: str
    status: str = "pending"
    twilio_message_sid: str | None = None
    error_message: str | None = None
    id: UUID = field(default_factory=uuid4)
    sent_at: datetime = field(default_factory=datetime.utcnow)
