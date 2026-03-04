from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Recipe:
    title: str
    ingredients: str
    instructions: str
    source_url: str | None = None
    image_url: str | None = None
    source_site: str | None = None
    ai_generated: bool = True
    id: UUID = field(default_factory=uuid4)
    protein_ids: list[UUID] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
