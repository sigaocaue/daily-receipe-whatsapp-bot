import json
import logging

import httpx
from openai import AsyncOpenAI

from config import settings
from src.domain.entities.recipe import Recipe
from src.domain.services.recipe_service import RecipeGeneratorService

logger = logging.getLogger(__name__)

RECIPE_PROMPT = """Você é um assistente culinário especializado em receitas brasileiras.

Gere uma receita real e deliciosa usando a proteína: {protein_name}.
Não gere as receitas a seguir: {existing_recipes}.

Retorne SOMENTE um JSON válido com esta estrutura:
{{
  "title": "Nome da Receita",
  "ingredients": "Lista resumida dos ingredientes principais",
  "instructions": "Modo de preparo detalhado mas conciso",
  "source_url": "https://www.tudogostoso.com.br/receita/...",
  "source_site": "TudoGostoso"
}}

A receita deve existir em sites reais como TudoGostoso, Panelinha, Receitas de Minuto, etc."""


class OpenAIRecipeGenerator(RecipeGeneratorService):
    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._unsplash_key = settings.UNSPLASH_ACCESS_KEY

    async def generate_recipe(
        self,
        protein_name: str,
        existing_recipe_titles: list[str],
    ) -> Recipe:
        existing = ", ".join(existing_recipe_titles) if existing_recipe_titles else "nenhuma"
        prompt = RECIPE_PROMPT.format(
            protein_name=protein_name,
            existing_recipes=existing,
        )

        logger.info("Requesting recipe from OpenAI for protein: %s", protein_name)
        response = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.8,
        )

        content = response.choices[0].message.content
        logger.info("OpenAI response received")

        data = json.loads(content)
        return Recipe(
            title=data["title"],
            ingredients=data["ingredients"],
            instructions=data["instructions"],
            source_url=data.get("source_url"),
            source_site=data.get("source_site"),
            ai_generated=True,
        )

    async def fetch_image_url(self, query: str) -> str | None:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": query, "per_page": 1, "orientation": "landscape"},
                    headers={"Authorization": f"Client-ID {self._unsplash_key}"},
                )
                response.raise_for_status()
                data = response.json()
                if data["results"]:
                    return data["results"][0]["urls"]["regular"]
        except Exception as e:
            logger.warning("Failed to fetch image from Unsplash: %s", e)
        return None
