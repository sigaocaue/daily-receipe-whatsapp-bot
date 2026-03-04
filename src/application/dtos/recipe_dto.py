from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateRecipeDTO:
    title: str
    ingredients: str
    instructions: str
    source_url: str | None = None
    image_url: str | None = None
    source_site: str | None = None
    ai_generated: bool = False
    protein_ids: list[UUID] | None = None


@dataclass
class UpdateRecipeDTO:
    title: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    source_url: str | None = None
    image_url: str | None = None
    source_site: str | None = None


@dataclass
class GenerateRecipeDTO:
    protein_ids: list[UUID] | None = None
