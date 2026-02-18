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
        from sqlalchemy import select, delete

        # Clear existing data as per user request (items currently in DB are unused)
        # This will cascade delete items due to relationship settings
        await session.execute(delete(Category))
        await session.flush()

        # Seed data based on "Start Cooperation" (Helper V2) structure
        seed_data = {
            "⚜️ سلامت پیشگیرانه": [
                "🚨 تماس اضطراری",
                "📋 سنجش سلامت",
                "🧠 غربالگری آلزایمر",
                "🏥 چکاپ‌های تخصصی",
                "🏠 بازطراحی محیط زندگی سالمندان"
            ],
            "⚜️ تجربه لحظه‌های به‌یاد ماندنی از راه‌دور": [
                "🍽️ سور (مهمان‌کردن و ساخت تجربه)",
                "🎶 سورپرایز (اجرای غافلگیرکننده)",
                "🌸 خرید هدیه، گل و شیرینی"
            ],
            "⚜️ انجام نیازهای روزمره": [
                "🧺 خرید روزمره",
                "💻 حل مشکلات دیجیتالی"
            ],
            "⚜️ میخوام .....": [
                "می‌خوام پیگیر وضعیت سلامت خانواده و عزیزان باشم!",
                "می‌خوام خانواده یا یکی از عزیزانم رو سوپرایز یا خوشحال کنم!",
                "میخوام برای خانوده یا یکی از عزیزانم هدیه، گل یا شیرینی ارسال کنم!",
                "نیاز به همیاری دارن و من از راه دور نمی‌تونم انجامش بدم!",
                "اونی که می‌خوام اینحا نیست!"
            ]
        }

        for cat_title, items in seed_data.items():
            cat = Category(title=cat_title)
            session.add(cat)
            await session.flush()  # Need ID for items
            
            for item_title in items:
                session.add(Item(category_id=cat.id, title=item_title))
        
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
