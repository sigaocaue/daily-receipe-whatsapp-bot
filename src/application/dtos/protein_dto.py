from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateProteinDTO:
    name: str
    active: bool = True


@dataclass
class UpdateProteinDTO:
    name: str | None = None
    active: bool | None = None


@dataclass
class ProteinResponseDTO:
    id: UUID
    name: str
    active: bool
