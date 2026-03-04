import os
import ssl as _ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

_NO_SSL_VALUES = {"disable", "allow", "false", "0", "no"}
_STRIP_PARAMS = {"sslmode", "ssl", "channel_binding", "gssencmode", "target_session_attrs", "sslnegotiation"}


def _normalize_database_url(raw_database_url: str) -> tuple[str, bool]:
    """Strip query params that asyncpg doesn't understand and return (url, use_ssl)."""
    parsed = urlparse(raw_database_url)
    query = parse_qs(parsed.query)

    sslmode = query.get("sslmode", [""])[0].strip().strip("'\"").lower()
    use_ssl = sslmode not in _NO_SSL_VALUES

    # Remove params unsupported by asyncpg.
    clean_query = {k: v[0] for k, v in query.items() if k not in _STRIP_PARAMS}

    # Ensure the scheme uses asyncpg driver.
    scheme = parsed.scheme
    if scheme.startswith("postgresql") and "+asyncpg" not in scheme:
        scheme = "postgresql+asyncpg"

    clean_url = urlunparse((
        scheme,
        parsed.netloc,  # preserves user:pass@host:port exactly
        parsed.path,
        parsed.params,
        urlencode(clean_query) if clean_query else "",
        "",
    ))

    return clean_url, use_ssl


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
    # Use "require" so asyncpg handles SSL negotiation itself (equivalent to sslmode=require).
    _connect_args["ssl"] = "require"

engine = create_async_engine(_clean_url, echo=False, connect_args=_connect_args)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
