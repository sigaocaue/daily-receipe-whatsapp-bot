import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.database.connection import Base


class MessageLogModel(Base):
    __tablename__ = "message_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    recipe_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recipes.id"), nullable=False)
    phone_number_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("phone_numbers.id"), nullable=False
    )
    message_content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    twilio_message_sid: Mapped[str | None] = mapped_column(String(255))
    error_message: Mapped[str | None] = mapped_column(Text)

    recipe = relationship("RecipeModel", back_populates="message_logs")
    phone_number = relationship("PhoneNumberModel", back_populates="message_logs")
