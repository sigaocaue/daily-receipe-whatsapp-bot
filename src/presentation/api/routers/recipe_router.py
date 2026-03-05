import logging
from uuid import UUID
from types import NoneType

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

import httpx

from src.application.dtos.recipe_dto import CreateRecipeDTO, GenerateRecipeDTO, ScrapeRecipeDTO, UpdateRecipeDTO
from src.application.use_cases.recipe.create_recipe_use_case import CreateRecipeUseCase
from src.application.use_cases.recipe.delete_recipe_use_case import DeleteRecipeUseCase
from src.application.use_cases.recipe.generate_recipe_use_case import GenerateRecipeUseCase
from src.application.use_cases.recipe.get_recipe_use_case import GetRecipeUseCase
from src.application.use_cases.recipe.list_recipes_use_case import ListRecipesUseCase
from src.application.use_cases.recipe.scrape_recipe_use_case import ScrapeRecipeUseCase
from src.application.use_cases.recipe.update_recipe_use_case import UpdateRecipeUseCase
from google.genai.errors import ClientError as GeminiClientError
from openai import RateLimitError as OpenAIRateLimitError

from config import settings
from src.domain.services.recipe_service import RecipeGeneratorService
from src.infrastructure.ai.gemini_recipe_generator import GeminiRecipeGenerator
from src.infrastructure.ai.openai_recipe_generator import OpenAIRecipeGenerator


def _get_recipe_generator() -> RecipeGeneratorService:
    if settings.AI_PROVIDER.lower() == "openai":
        return OpenAIRecipeGenerator()
    return GeminiRecipeGenerator()
from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_protein_repository import (
    SQLAlchemyProteinRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)
from src.infrastructure.scraping.tudo_gostoso_scraper import TudoGostosoScraper
from src.presentation.api.schemas.recipe_schema import (
    GenerateRecipeRequest,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
    ScrapeRecipeRequest,
)
from src.presentation.api.schemas.response_schema import ApiResponse

router = APIRouter(prefix="/api/v1/recipes", tags=["Recipes"])


def _recipe_response(recipe) -> RecipeResponse:
    return RecipeResponse(
        id=recipe.id,
        title=recipe.title,
        ingredients=recipe.ingredients,
        instructions=recipe.instructions,
        source_url=recipe.source_url,
        image_url=recipe.image_url,
        source_site=recipe.source_site,
        ai_generated=recipe.ai_generated,
        protein_ids=recipe.protein_ids,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
    )


@router.post(
    "",
    response_model=ApiResponse[RecipeResponse],
    status_code=201,
    summary="Criar receita",
    description="Cadastra uma nova receita manualmente com título, ingredientes e instruções.",
)
async def create_recipe(body: RecipeCreate, session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = CreateRecipeUseCase(repo)
    recipe = await use_case.execute(
        CreateRecipeDTO(
            title=body.title,
            ingredients=body.ingredients,
            instructions=body.instructions,
            source_url=body.source_url,
            image_url=body.image_url,
            source_site=body.source_site,
            ai_generated=body.ai_generated,
            protein_ids=body.protein_ids,
        )
    )
    return {"data": _recipe_response(recipe), "message": "Recipe created"}


@router.get(
    "",
    response_model=ApiResponse[list[RecipeResponse]],
    summary="Listar receitas",
    description="Retorna todas as receitas cadastradas (manuais e geradas por IA).",
)
async def list_recipes(session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = ListRecipesUseCase(repo)
    recipes = await use_case.execute()
    return {"data": [_recipe_response(r) for r in recipes], "message": "Recipes listed"}


@router.post(
    "/generate",
    response_model=ApiResponse[RecipeResponse],
    status_code=201,
    summary="Gerar receita via IA",
    description=(
        "Gera uma nova receita automaticamente usando OpenAI GPT-4o. "
        "Opcionalmente, pode receber uma lista de IDs de proteínas para direcionar a geração. "
        "O sistema evita repetir as últimas 5 receitas enviadas."
    ),
    responses={400: {"description": "Nenhuma proteína ativa encontrada ou erro na geração"}},
)
async def generate_recipe(
    body: GenerateRecipeRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    recipe_repo = SQLAlchemyRecipeRepository(session)
    protein_repo = SQLAlchemyProteinRepository(session)
    generator = _get_recipe_generator()

    use_case = GenerateRecipeUseCase(recipe_repo, protein_repo, generator)
    try:
        recipe = await use_case.execute(
            GenerateRecipeDTO(protein_ids=body.protein_ids if body else None)
        )
    except ValueError as e:
        logger.warning("ValueError during recipe generation: %s", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except OpenAIRateLimitError as e:
        logger.warning("OpenAI quota exceeded: %s", e)
        raise HTTPException(status_code=429, detail="Cota da API excedida. Tente novamente mais tarde.")
    except GeminiClientError as e:
        if e.code == 429:
            logger.warning("Gemini quota exceeded: %s", e)
            raise HTTPException(status_code=429, detail="Cota da API excedida. Tente novamente mais tarde.")
        logger.error("Gemini client error during recipe generation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro inesperado ao gerar a receita.")
    except Exception as e:
        logger.error("Unexpected error during recipe generation: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro inesperado ao gerar a receita.")
    return {"data": _recipe_response(recipe), "message": "Recipe generated via AI"}


@router.post(
    "/scrape",
    response_model=ApiResponse[RecipeResponse],
    status_code=201,
    summary="Importar receita do TudoGostoso",
    description=(
        "Importa uma receita do site TudoGostoso via web scraping. "
        "Se uma URL for fornecida, busca a receita específica. "
        "Caso contrário, busca uma receita aleatória."
    ),
    responses={
        400: {"description": "URL inválida ou erro ao buscar receita"},
        502: {"description": "Erro de comunicação com o serviço de scraping"},
    },
)
async def scrape_recipe(
    body: ScrapeRecipeRequest | None = None,
    session: AsyncSession = Depends(get_session),
):
    recipe_repo = SQLAlchemyRecipeRepository(session)
    scraper = TudoGostosoScraper()
    use_case = ScrapeRecipeUseCase(recipe_repo, scraper)
    try:
        recipe = await use_case.execute(
            ScrapeRecipeDTO(url=body.url if body else None)
        )
    except httpx.HTTPStatusError as e:
        logger.warning("Scraper API returned error: %s", e)
        raise HTTPException(status_code=502, detail="Erro ao buscar receita do TudoGostoso.")
    except httpx.RequestError as e:
        logger.error("Scraper API connection error: %s", e)
        raise HTTPException(status_code=502, detail="Não foi possível conectar ao serviço de scraping.")
    except KeyError as e:
        logger.error("Unexpected scraper response format: missing key %s", e)
        raise HTTPException(status_code=502, detail="Resposta inesperada do serviço de scraping.")
    except Exception as e:
        logger.error("Unexpected error during recipe scraping: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Erro inesperado ao importar a receita.")
    return {"data": _recipe_response(recipe), "message": "Receita importada do TudoGostoso"}


@router.get(
    "/{recipe_id}",
    response_model=ApiResponse[RecipeResponse],
    summary="Buscar receita por ID",
    description="Retorna uma receita específica pelo seu UUID.",
    responses={404: {"description": "Receita não encontrada"}},
)
async def get_recipe(recipe_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = GetRecipeUseCase(repo)
    recipe = await use_case.execute(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"data": _recipe_response(recipe), "message": "Recipe found"}


@router.patch(
    "/{recipe_id}",
    response_model=ApiResponse[RecipeResponse],
    summary="Atualizar receita",
    description="Atualiza parcialmente uma receita existente.",
    responses={404: {"description": "Receita não encontrada"}},
)
async def update_recipe(
    recipe_id: UUID, body: RecipeUpdate, session: AsyncSession = Depends(get_session)
):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = UpdateRecipeUseCase(repo)
    recipe = await use_case.execute(
        recipe_id,
        UpdateRecipeDTO(
            title=body.title,
            ingredients=body.ingredients,
            instructions=body.instructions,
            source_url=body.source_url,
            image_url=body.image_url,
            source_site=body.source_site,
        ),
    )
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"data": _recipe_response(recipe), "message": "Recipe updated"}


@router.delete(
    "/{recipe_id}",
    response_model=ApiResponse[NoneType],
    summary="Excluir receita",
    description="Remove permanentemente uma receita pelo seu UUID.",
    responses={404: {"description": "Receita não encontrada"}},
)
async def delete_recipe(recipe_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = SQLAlchemyRecipeRepository(session)
    use_case = DeleteRecipeUseCase(repo)
    deleted = await use_case.execute(recipe_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"data": None, "message": "Recipe deleted"}
