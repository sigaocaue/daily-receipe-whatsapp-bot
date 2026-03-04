from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecipeCreate(BaseModel):
    title: str
    ingredients: str
    instructions: str
    source_url: str | None = None
    image_url: str | None = None
    source_site: str | None = None
    ai_generated: bool = False
    protein_ids: list[UUID] | None = None


class RecipeUpdate(BaseModel):
    title: str | None = None
    ingredients: str | None = None
    instructions: str | None = None
    source_url: str | None = None
    image_url: str | None = None
    source_site: str | None = None


class GenerateRecipeRequest(BaseModel):
    protein_ids: list[UUID] | None = None


class RecipeResponse(BaseModel):
    id: UUID
    title: str
    ingredients: str
    instructions: str
    source_url: str | None
    image_url: str | None
    source_site: str | None
    ai_generated: bool
    protein_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
