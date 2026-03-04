from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dtos.recipe_dto import CreateRecipeDTO, GenerateRecipeDTO, UpdateRecipeDTO
from src.application.use_cases.generate_recipe_use_case import GenerateRecipeUseCase
from src.application.use_cases.list_recipes_use_case import (
    CreateRecipeUseCase,
    DeleteRecipeUseCase,
    GetRecipeUseCase,
    ListRecipesUseCase,
    UpdateRecipeUseCase,
)
from src.infrastructure.ai.openai_recipe_generator import OpenAIRecipeGenerator
from src.infrastructure.database.connection import get_session
from src.infrastructure.database.repositories.sqlalchemy_protein_repository import (
    SQLAlchemyProteinRepository,
)
from src.infrastructure.database.repositories.sqlalchemy_recipe_repository import (
    SQLAlchemyRecipeRepository,
)
from src.presentation.api.schemas.recipe_schema import (
    GenerateRecipeRequest,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
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
    response_model=ApiResponse[None],
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
    generator = OpenAIRecipeGenerator()

    use_case = GenerateRecipeUseCase(recipe_repo, protein_repo, generator)
    try:
        recipe = await use_case.execute(
            GenerateRecipeDTO(protein_ids=body.protein_ids if body else None)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"data": _recipe_response(recipe), "message": "Recipe generated via AI"}
