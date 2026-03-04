import logging

from fastapi import FastAPI

from src.infrastructure.logging.logger import setup_logging
from src.presentation.api.routers.message_router import router as message_router
from src.presentation.api.routers.phone_number_router import router as phone_number_router
from src.presentation.api.routers.protein_router import router as protein_router
from src.presentation.api.routers.recipe_router import router as recipe_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Daily Recipe WhatsApp Bot",
    description="API backend que envia receitas culinárias diárias via WhatsApp",
    version="0.1.0",
)

app.include_router(protein_router)
app.include_router(recipe_router)
app.include_router(phone_number_router)
app.include_router(message_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"data": {"status": "healthy"}, "message": "Application is running"}


@app.on_event("startup")
async def startup_event():
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
