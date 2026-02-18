from __future__ import annotations

import os
import pathlib
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from db.models import Base, Category, Item, User


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
    await _seed_initial_data()
    await _ensure_order_columns()
    await _seed_admin_user()


def get_session() -> AsyncSession:
    if SessionLocal is None:
        raise RuntimeError("DB not initialized")
    return SessionLocal()


async def _seed_initial_data() -> None:
    if SessionLocal is None:
        return
    async with SessionLocal() as session:
        # Check if categories exist
        from sqlalchemy import select

        res = await session.execute(select(Category))
        existing = list(res.scalars().all())
        if existing:
            return

        # Seed categories
        cat_titles = [
            "⚜️ سلامت پیشگیرانه ⚜️",
            "⚜️ ساخت لحظه‌های به‌یاد ماندنی از راه‌دور ⚜️",
            "⚜️ انجام نیازهای روزمره ⚜️",
            "⚜️ میخـوام ... ⚜️",
        ]
        cats: list[Category] = [Category(title=t) for t in cat_titles]
        session.add_all(cats)
        await session.flush()

        # Seed items per category (aligning with previous options)
        items_by_idx = {
            0: ["", "", ""],
            1: ["", "", ""],
            2: ["", "", ""],
            3: ["", "", ""],
        }
        for idx, cat in enumerate(cats):
            titles = items_by_idx.get(idx, [])
            session.add_all([Item(category_id=cat.id, title=t) for t in titles])
        await session.commit()


async def _seed_admin_user() -> None:
    if SessionLocal is None:
        return
    async with SessionLocal() as session:
        from sqlalchemy import select
        res = await session.execute(select(User).where(User.telegram_id == 1030212127))
        user = res.scalars().first()
        if user:
            return
        admin = User(
            telegram_id=1030212127,
            username="Shahram0weisy",
            full_name="shahram oweisy",
            role_id=1,
        )
        session.add(admin)
        await session.commit()


async def _ensure_order_columns() -> None:
    if SessionLocal is None:
        return
    async with SessionLocal() as session:
        result = await session.execute(text("PRAGMA table_info('orders')"))
        cols = {row[1] for row in result.fetchall()}
        alters: list[str] = []
        if 'phone_number' not in cols:
            alters.append("ALTER TABLE orders ADD COLUMN phone_number VARCHAR(32)")
        if 'full_name' not in cols:
            alters.append("ALTER TABLE orders ADD COLUMN full_name VARCHAR(128)")
        if 'username' not in cols:
            alters.append("ALTER TABLE orders ADD COLUMN username VARCHAR(64)")
        if 'done_at' not in cols:
            alters.append("ALTER TABLE orders ADD COLUMN done_at TIMESTAMP NULL")
        for sql in alters:
            try:
                await session.execute(text(sql))
            except Exception:
                pass
        if alters:
            await session.commit()
