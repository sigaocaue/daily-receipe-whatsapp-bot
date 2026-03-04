import asyncio
import logging

from sqlalchemy import select

from src.infrastructure.database.connection import async_session
from src.infrastructure.database.models import PhoneNumberModel, ProteinModel
from src.infrastructure.logging.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

INITIAL_PROTEINS = [
    "Frango",
    "Carne moída de patinho",
    "Carne moída de coxão duro",
    "Salmão",
    "Atum",
    "Bife Patinho",
    "Bife Contra Filé",
]

INITIAL_PHONE_NUMBERS = [
    {"name": "Sara (esposa)", "phone": "+5511975408216", "active": True},
]


async def seed():
    async with async_session() as session:
        # Seed proteins
        for protein_name in INITIAL_PROTEINS:
            exists = await session.execute(
                select(ProteinModel).where(ProteinModel.name == protein_name)
            )
            if not exists.scalar_one_or_none():
                session.add(ProteinModel(name=protein_name, active=True))
                logger.info("Added protein: %s", protein_name)
            else:
                logger.info("Protein already exists: %s", protein_name)

        # Seed phone numbers
        for phone_data in INITIAL_PHONE_NUMBERS:
            exists = await session.execute(
                select(PhoneNumberModel).where(PhoneNumberModel.phone == phone_data["phone"])
            )
            if not exists.scalar_one_or_none():
                session.add(PhoneNumberModel(**phone_data))
                logger.info("Added phone number: %s", phone_data["phone"])
            else:
                logger.info("Phone number already exists: %s", phone_data["phone"])

        await session.commit()
        logger.info("Seed completed successfully")


if __name__ == "__main__":
    asyncio.run(seed())
