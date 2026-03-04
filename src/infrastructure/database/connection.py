from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from config import settings


def _normalize_database_url(raw_database_url: str) -> str:
    url = make_url(raw_database_url)
    query = dict(url.query)

    # Render and other providers often expose PostgreSQL URLs with libpq params.
    # asyncpg does not accept all of them, so normalize/strip incompatible keys.
    if "sslmode" in query and "ssl" not in query:
        sslmode = str(query.pop("sslmode")).lower()
        query["ssl"] = "false" if sslmode in {"disable", "allow"} else "true"

    # Parameters below are valid in libpq/psycopg URLs but unsupported by asyncpg.
    for key in ("channel_binding", "gssencmode", "target_session_attrs", "sslnegotiation"):
        query.pop(key, None)

    return str(url.set(query=query))


engine = create_async_engine(_normalize_database_url(settings.DATABASE_URL), echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
