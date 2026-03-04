from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from config import settings

def _normalize_database_url(raw_database_url: str) -> str:
    url = make_url(raw_database_url)
    query = dict(url.query)

    # Render and other providers often expose PostgreSQL URLs with `sslmode`.
    # asyncpg expects the `ssl` argument, so translate to keep production compatible.
    if "sslmode" in query and "ssl" not in query:
        sslmode = str(query.pop("sslmode")).lower()
        query["ssl"] = "false" if sslmode in {"disable", "allow"} else "true"

    return str(url.set(query=query))


engine = create_async_engine(_normalize_database_url(settings.DATABASE_URL), echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
