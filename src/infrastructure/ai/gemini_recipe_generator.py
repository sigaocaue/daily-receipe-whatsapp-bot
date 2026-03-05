import json
import logging

from google import genai
from google.genai.types import GenerateContentConfig

from config import settings
from src.domain.entities.recipe import Recipe
from src.domain.services.recipe_service import RecipeGeneratorService
from src.infrastructure.ai.unsplash_image_fetcher_mixin import UnsplashImageFetcherMixin

logger = logging.getLogger(__name__)

RECIPE_PROMPT = """Voce e um assistente culinario especializado em receitas brasileiras.

Gere uma receita real e deliciosa usando a proteina: {protein_name}.
Nao gere as receitas a seguir: {existing_recipes}.

Retorne SOMENTE um JSON valido com esta estrutura:
{{
  "title": "Nome da Receita",
  "ingredients": "Lista resumida dos ingredientes principais",
  "instructions": "Modo de preparo detalhado mas conciso",
  "source_url": "https://www.tudogostoso.com.br/receita/...",
  "source_site": "TudoGostoso"
}}

A receita deve existir em sites reais como TudoGostoso, Panelinha, Receitas de Minuto, etc."""


class GeminiRecipeGenerator(UnsplashImageFetcherMixin, RecipeGeneratorService):
    def __init__(self):
        self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
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

        logger.info("Requesting recipe from Gemini for protein: %s", protein_name)
        response = await self._client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8,
            ),
        )

        content = response.text
        logger.info("Gemini response received")

        data = json.loads(content)
        logger.info(f"The Gemini are: {data}")
        return Recipe(
            title=data["title"],
            ingredients=data["ingredients"],
            instructions=data["instructions"],
            source_url=data.get("source_url"),
            source_site=data.get("source_site"),
            ai_generated=True,
        )
