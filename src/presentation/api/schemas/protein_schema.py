from uuid import UUID

from pydantic import BaseModel


class ProteinCreate(BaseModel):
    name: str
    active: bool = True


class ProteinUpdate(BaseModel):
    name: str | None = None
    active: bool | None = None


class ProteinResponse(BaseModel):
    id: UUID
    name: str
    active: bool

    model_config = {"from_attributes": True}
