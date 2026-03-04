import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from config import settings


def _normalize_database_url(raw_database_url: str) -> str:
    url = make_url(raw_database_url)
    query = dict(url.query)

    # asyncpg accepts sslmode with these values; keep it as-is when valid.
    _ASYNCPG_SSLMODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}

    sslmode = str(query.get("sslmode", "")).strip().strip("'\"").lower()
    if sslmode and sslmode not in _ASYNCPG_SSLMODES:
        # Non-standard value — replace with a safe default.
        query["sslmode"] = "require"

    # Parameters below are valid in libpq/psycopg URLs but unsupported by asyncpg.
    for key in ("channel_binding", "gssencmode", "target_session_attrs", "sslnegotiation"):
        query.pop(key, None)

    return str(url.set(query=query))


# Some platforms inject PG* variables with libpq semantics that asyncpg rejects.
for key in (
    "PGSSLMODE",
    "PGCHANNELBINDING",
    "PGGSSENCMODE",
    "PGTARGETSESSIONATTRS",
    "PGSSLNEGOTIATION",
):
    os.environ.pop(key, None)

engine = create_async_engine(_normalize_database_url(settings.DATABASE_URL), echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
