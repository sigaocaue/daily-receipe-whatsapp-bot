from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PhoneNumberCreate(BaseModel):
    name: str | None = None
    phone: str
    active: bool = True


class PhoneNumberUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    active: bool | None = None


class PhoneNumberResponse(BaseModel):
    id: UUID
    name: str | None
    phone: str
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
