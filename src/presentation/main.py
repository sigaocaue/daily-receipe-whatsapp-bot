import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from src.infrastructure.logging.logger import setup_logging
from src.presentation.api.routers.message_router import router as message_router
from src.presentation.api.routers.phone_number_router import router as phone_number_router
from src.presentation.api.routers.protein_router import router as protein_router
from src.presentation.api.routers.recipe_router import router as recipe_router

setup_logging()
logger = logging.getLogger(__name__)

tags_metadata = [
    {
        "name": "Health",
        "description": "Verificação de saúde da aplicação.",
    },
    {
        "name": "Proteins",
        "description": "Gerenciamento de proteínas disponíveis para geração de receitas.",
    },
    {
        "name": "Recipes",
        "description": "CRUD de receitas e geração automática via IA (OpenAI GPT-4o).",
    },
    {
        "name": "Phone Numbers",
        "description": "Gerenciamento de números de telefone destinatários das receitas via WhatsApp.",
    },
    {
        "name": "Messages",
        "description": "Envio de receitas via WhatsApp (Twilio) e consulta ao histórico de mensagens.",
    },
]

app = FastAPI(
    title="Daily Recipe WhatsApp Bot",
    description=(
        "API backend que envia receitas culinárias diárias via WhatsApp.\n\n"
        "## Funcionalidades\n"
        "- **Proteínas**: cadastro e gerenciamento de proteínas\n"
        "- **Receitas**: CRUD e geração automática via OpenAI GPT-4o\n"
        "- **Números**: gerenciamento de destinatários WhatsApp\n"
        "- **Mensagens**: envio de receitas e histórico de envios"
    ),
    version="0.1.0",
    openapi_tags=tags_metadata,
)

allowed_origins = [origin.strip() for origin in settings.CORS_ALLOW_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(protein_router)
app.include_router(recipe_router)
app.include_router(phone_number_router)
app.include_router(message_router)


@app.get("/health", tags=["Health"], summary="Health check", description="Retorna o status da aplicação.")
async def health_check():
    return {"data": {"status": "healthy"}, "message": "Application is running"}


@app.on_event("startup")
async def startup_event():
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
