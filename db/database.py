from __future__ import annotations

import os
import pathlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from db.models import Base


_engine: Optional[AsyncEngine] = None
SessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def _extract_sqlite_path(db_url: str) -> Optional[pathlib.Path]:
    if db_url.startswith("sqlite+aiosqlite:///"):
        path = db_url.split("sqlite+aiosqlite:///", 1)[1]
        return pathlib.Path(path)
    return None


async def init_db(db_url: Optional[str] = None) -> None:
    global _engine, SessionLocal
    url = db_url or os.getenv("DB_URL", "sqlite+aiosqlite:///./data/app.db")
    p = _extract_sqlite_path(url)
    if p:
        p.parent.mkdir(parents=True, exist_ok=True)
    _engine = create_async_engine(url, echo=False, future=True)
    SessionLocal = async_sessionmaker(_engine, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("SELECT 1"))


def get_session() -> AsyncSession:
    if SessionLocal is None:
        raise RuntimeError("DB not initialized")
    return SessionLocal()

