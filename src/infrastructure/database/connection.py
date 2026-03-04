import os
import ssl as _ssl

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase

from config import settings

_NO_SSL_VALUES = {"disable", "allow", "false", "0", "no"}


def _normalize_database_url(raw_database_url: str) -> tuple[str, bool]:
    """Strip query params that asyncpg doesn't understand and return (url, use_ssl)."""
    url = make_url(raw_database_url)
    query = dict(url.query)

    sslmode = str(query.pop("sslmode", "")).strip().strip("'\"").lower()
    use_ssl = sslmode not in _NO_SSL_VALUES

    # Parameters below are valid in libpq/psycopg URLs but unsupported by asyncpg.
    for key in ("ssl", "channel_binding", "gssencmode", "target_session_attrs", "sslnegotiation"):
        query.pop(key, None)

    # Ensure the URL always uses the asyncpg driver.
    if url.get_backend_name() == "postgresql" and "+asyncpg" not in url.drivername:
        url = url.set(drivername="postgresql+asyncpg")

    return str(url.set(query=query)), use_ssl


# Some platforms inject PG* variables with libpq semantics that asyncpg rejects.
for key in (
    "PGSSLMODE",
    "PGCHANNELBINDING",
    "PGGSSENCMODE",
    "PGTARGETSESSIONATTRS",
    "PGSSLNEGOTIATION",
):
    os.environ.pop(key, None)

_clean_url, _use_ssl = _normalize_database_url(settings.DATABASE_URL)

_connect_args: dict = {}
if _use_ssl:
    _ctx = _ssl.create_default_context()
    _ctx.check_hostname = False
    _ctx.verify_mode = _ssl.CERT_NONE
    _connect_args["ssl"] = _ctx

engine = create_async_engine(_clean_url, echo=False, connect_args=_connect_args)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
